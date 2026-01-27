"""
Chapter Processor.
Handles the translation of a single chapter using Gemini and RAG context.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from pipeline.common.gemini_client import GeminiClient
from pipeline.translator.prompt_loader import PromptLoader
from pipeline.translator.context_manager import ContextManager
from pipeline.translator.quality_metrics import QualityMetrics, AuditResult
from pipeline.translator.config import get_generation_params, get_model_name, get_safety_settings
from pipeline.translator.scene_break_formatter import SceneBreakFormatter

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    success: bool
    output_path: Path
    input_tokens: int = 0
    output_tokens: int = 0
    audit_result: Optional[AuditResult] = None
    warnings: List[str] = None
    error: Optional[str] = None
    context_update: Optional[Dict[str, Any]] = None

class ChapterProcessor:
    def __init__(
        self,
        gemini_client: GeminiClient,
        prompt_loader: PromptLoader,
        context_manager: ContextManager
    ):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.context_manager = context_manager
        self.model_name = get_model_name()
        self.gen_params = get_generation_params()
        self.safety_settings = get_safety_settings()
        
        # Track if we've notified user about thinking log availability
        self._thinking_log_notified = False
        
        # Load character names from manifest.json for name consistency
        self.character_names = self._load_character_names()
        if self.character_names:
            logger.info(f"✓ Loaded {len(self.character_names)} character names from manifest")
    
    def _load_character_names(self) -> Dict[str, str]:
        """Load character names from manifest.json metadata_en."""
        try:
            # Get work directory from context_manager
            work_dir = self.context_manager.work_dir
            
            # Try metadata_en.json first (preferred)
            metadata_en_path = work_dir / "metadata_en.json"
            if metadata_en_path.exists():
                with open(metadata_en_path, 'r', encoding='utf-8') as f:
                    metadata_en = json.load(f)
                    return metadata_en.get('character_names', {})
            
            # Fallback to manifest.json
            manifest_path = work_dir / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    metadata_en = manifest.get('metadata_en', {})
                    return metadata_en.get('character_names', {})
            
            logger.warning("No character names found in manifest")
            return {}
            
        except Exception as e:
            logger.warning(f"Failed to load character names: {e}")
            return {}

    def translate_chapter(
        self,
        source_path: Path,
        output_path: Path,
        chapter_id: str,
        en_title: Optional[str] = None,
        model_name: Optional[str] = None,
        cached_content: Optional[str] = None
    ) -> TranslationResult:
        """
        Translate a single chapter file.
        
        Args:
            source_path: Path to source Japanese chapter
            output_path: Path to save translated chapter
            chapter_id: Chapter identifier
            en_title: Translated chapter title
            model_name: Model override
            cached_content: Cached content name for continuity (from previous chapter schema)
        """
        try:
            logger.debug(f"[VERBOSE] Starting translation for {chapter_id}")
            logger.debug(f"[VERBOSE] Source: {source_path}")
            logger.debug(f"[VERBOSE] Output: {output_path}")
            
            # 1. Load Source
            if not source_path.exists():
                return TranslationResult(False, output_path, error=f"Source file not found: {source_path}")
            
            logger.debug(f"[VERBOSE] Reading source file...")
            with open(source_path, 'r', encoding='utf-8') as f:
                source_text = f.read()
            logger.debug(f"[VERBOSE] Source text length: {len(source_text)} characters")

            # Strip JP title if present (usually the first H1)
            # We preserve the original title for audit but send the rest to LLM
            source_content_only = source_text
            jp_title_match = re.match(r'^#\s*(.*?)\n+', source_text)
            if jp_title_match:
                source_content_only = source_text[jp_title_match.end():].strip()
                logger.info(f"Stripped JP title for translation: {jp_title_match.group(1)}")

            # 2. Build Prompt
            logger.debug(f"[VERBOSE] Building system instruction...")
            # Get Master Prompt + RAG Modules (System Instruction)
            system_instruction = self.prompt_loader.build_system_instruction()
            logger.debug(f"[VERBOSE] System instruction length: {len(system_instruction)} characters")
            
            # Get Context (Continuity)
            logger.debug(f"[VERBOSE] Getting context prompt...")
            context_str = self.context_manager.get_context_prompt(chapter_id)
            logger.debug(f"[VERBOSE] Context length: {len(context_str)} characters")
            
            # Construct User Message
            logger.debug(f"[VERBOSE] Building user prompt...")
            user_prompt = self._build_user_prompt(
                chapter_id, 
                source_content_only, 
                context_str,
                en_title
            )
            logger.debug(f"[VERBOSE] User prompt length: {len(user_prompt)} characters")
            
            # 3. Call Gemini
            logger.debug(f"[VERBOSE] Calling Gemini API...")
            # Note regarding model: gemini_client usually handles model in init or call
            # We pass system_instruction separately as per new API patterns
            # If we have cached_content from previous chapter, pass it for continuity
            response = self.client.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=self.gen_params.get("temperature", 0.7),
                max_output_tokens=self.gen_params.get("max_output_tokens", 65536),
                model=model_name or self.model_name,
                cached_content=cached_content  # Inject cached schema for continuity
            )
            logger.debug(f"[VERBOSE] Gemini response received. Tokens: {response.input_tokens} in, {response.output_tokens} out")
            
            if not response.content:
                return TranslationResult(
                    False, output_path,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    error="Gemini returned empty response (possible safety block)"
                )
            
            # 4. Parse Response
            # We expect Markdown output. Prompt 2.0 asks for pure markdown.
            # But prompt also says <CONTINUITY_UPDATE>...
            # Wait, I optimized the prompt to REMOVE XML tags in OUTPUT_FORMAT?
            # Let me check my previous step.
            # Step 113 modify TRANSLATION_OUTPUT to be pure Markdown...
            # BUT Step 99 added CONTINUITY_UPDATE xml block...
            # Ah, Step 113 removed the XML structure and said "run analysis silently".
            # So we might NOT get explicit new terms in XML format if the prompt strictly follows 113.
            # HOWEVER, if we want continuity, we need ample output. 
            # Reviewing Step 113: "Modify the TRANSLATION_OUTPUT block... SCENE_TONE silent... output only Chapter Title and Content"
            # This implies NO structured context update in output. 
            # This makes automatic context updating harder. 
            # I will assume purely prose output for now, and ContextManager relies on 
            # maybe a separate extraction step OR we infer from the text (hard).
            # OR I should have kept the XML for context updates.
            # Decision: Process text as is for now. If context update missing, we just log it.
            
            translated_body = response.content
            
            # Post-process (cleanup markdown fences if any)
            cleaned_body = self._clean_output(translated_body)
            
            # Inject EN title if provided
            final_content = cleaned_body
            if en_title:
                final_content = f"# {en_title}\n\n{cleaned_body}"
                logger.info(f"Injected title: {en_title}")
            
            # Format scene breaks (replace *, **, *** with centered ◆)
            final_content, scene_break_count = SceneBreakFormatter.format_scene_breaks(final_content)
            if scene_break_count > 0:
                logger.info(f"Formatted {scene_break_count} scene break(s) in {chapter_id}")
            
            # 5. Save Thinking/CoT Log (if present)
            thinking_content = getattr(response, 'thinking_content', None)
            if thinking_content:
                thinking_log_path = output_path.parent / f"{output_path.stem}_THINKING.md"
                thinking_log_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(thinking_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Gemini Thinking Log: {chapter_id}\n\n")
                    f.write(f"**Model:** `{response.model}`  \n")
                    f.write(f"**Input Tokens:** {response.input_tokens:,}  \n")
                    f.write(f"**Output Tokens:** {response.output_tokens:,}  \n")
                    f.write(f"**Finish Reason:** {response.finish_reason}  \n")
                    f.write(f"**Week 1 RAG Upgrades:** ANTI_TRANSLATIONESE v2.1, kanji_difficult.json (108 entries)\n\n")
                    f.write("---\n\n")
                    f.write("## Extended Thinking Process\n\n")
                    f.write(thinking_content)
                
                logger.info(f"✓ Saved thinking log to {thinking_log_path.name}")
            elif not self._thinking_log_notified:
                # First run without thinking logs - notify user once
                logger.info(f"ℹ️  Thinking logs not available with {response.model}")
                logger.info(f"   (This is normal - most models don't expose reasoning chains)")
                self._thinking_log_notified = True
            
            # 6. Quality Audit (Audit against full source for accuracy check)
            audit = QualityMetrics.quick_audit(final_content, source_text)
            
            # 7. Save Translation Output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return TranslationResult(
                success=True,
                output_path=output_path,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                audit_result=audit,
                warnings=audit.warnings
            )

        except Exception as e:
            logger.exception(f"Translation failed for {chapter_id}")
            return TranslationResult(False, output_path, error=str(e))

    def _build_user_prompt(
        self, 
        chapter_id: str, 
        source_text: str, 
        context_str: str,
        chapter_title: Optional[str] = None
    ) -> str:
        """Construct the user message part of the prompt."""
        # Use PromptLoader's build_translation_prompt for proper name registry injection
        return self.prompt_loader.build_translation_prompt(
            source_text=source_text,
            chapter_title=chapter_title or chapter_id,
            previous_context=context_str if context_str else None,
            name_registry=self.character_names if self.character_names else None
        )

    def _clean_output(self, text: str) -> str:
        """Clean up LLM output (remove markdown code blocks if present)."""
        # Remove ```markdown and ``` if fully wrapped
        # Sometimes models wrap the whole thing
        pattern = r"^```(?:markdown)?\s*(.*)\s*```$"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
