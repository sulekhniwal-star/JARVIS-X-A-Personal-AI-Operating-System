# TODO: Fix Pylint Errors

## Core Files
- [ ] Fix core/api_manager.py: Change broad exceptions to specific or disable, add missing docstrings
- [x] Fix core/assistant.py: Add docstrings, fix long lines, remove unused imports, fix unnecessary else, reduce locals, fix import order
- [ ] Fix core/google_generativeai_stub.pyi: Add docstrings, fix missing newline, unused args
- [ ] Fix core/intent_classifier.py: Add docstrings, fix long lines
- [ ] Fix core/life_automation.py: Add docstrings, fix long lines, unnecessary else, broad exception
- [ ] Fix core/life_os.py: Add docstrings, broad exception
- [ ] Fix core/llm.py: Add docstrings, broad exception
- [ ] Fix core/personality.py: Add docstrings, unnecessary elif, too many returns
- [ ] Fix core/safety.py: Add docstrings, fix long lines
- [ ] Fix core/self_coder.py: Add docstrings, broad exception
- [ ] Fix core/self_improver.py: Add docstrings, broad exception, f-string without interpolation, bare except
- [ ] Fix core/skill_learner.py: Add docstrings, broad exceptions, unnecessary else
- [ ] Fix core/skill_manager.py: Add docstrings, trailing newlines, too many nested blocks, unnecessary elif
- [ ] Fix core/skill_router.py: Add docstrings, broad exception, too many returns, wrong import order
- [ ] Fix core/speech_to_text.py: Add docstrings, pointless string, wrong import positions, logging f-strings, too many locals, broad exception, unused args
- [ ] Fix core/text_to_speech.py: Add docstrings, pointless string, wrong import positions, logging f-strings, broad exception, bare except
- [ ] Fix core/wake_word.py: Add docstrings, unused imports, long lines

## Skills Files
- [ ] Fix skills/email_sender.py: Add docstrings, broad exception
- [ ] Fix skills/entertainment.py: Fix long lines, broad exceptions, unnecessary elif, too many returns, no-member, wrong import order
- [ ] Fix skills/information.py: Fix long lines, broad exceptions, unnecessary elif, too many returns
- [ ] Fix skills/music.py: Fix long lines, broad exceptions, unnecessary else/elif, too many returns, import outside toplevel, unused import
- [ ] Fix skills/pc_control.py: Add docstrings, broad exceptions, no-member, protected access, consider with, wrong import order
- [ ] Fix skills/productivity.py: Fix long lines, broad exceptions, unnecessary elif, too many returns, import outside toplevel, unused imports, wrong import order
- [ ] Fix skills/small_talk.py: Unnecessary elif
- [ ] Fix skills/smart_home.py: Fix long lines, broad exceptions, unnecessary elif, too many returns, unused variable, unused args, import outside toplevel, unused import
- [ ] Fix skills/system_control.py: Broad exceptions, consider with
- [ ] Fix skills/timer_alarm.py: Fix long lines, broad exceptions, unnecessary else/elif, too many returns, unused variables, import outside toplevel, unused import
- [ ] Fix skills/web_search.py: Add docstrings, broad exception, unused import

## Utils Files
- [ ] Fix utils/file_indexer.py: Add docstrings, broad exception
- [ ] Fix utils/goals.py: Add docstrings
- [ ] Fix utils/memory.py: Add docstrings
- [ ] Fix utils/persistent_memory.py: Add docstrings, missing function docstrings
- [ ] Fix utils/routines.py: Add docstrings

## Main File
- [ ] Fix main.py: Broad exceptions, too many branches/statements, duplicate code

## Verification
- [ ] Run Pylint again to verify all errors are fixed
