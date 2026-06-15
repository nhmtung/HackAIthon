import os
import json
import logging
import ast
import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def load_questions(file_path: str) -> list[dict]:
    """
    Defensive question loader supporting JSON and CSV fallback.
    Conforms to AGENTS.md requirements:
    - Explicit encoding="utf-8"
    - Comprehensive error handling to prevent pipeline crashes
    - Returns list of clean question dicts: {"qid": ..., "question": ..., "choices": [...]}
    """
    questions: list[dict] = []
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return questions

    # Determine parser based on file extension
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read/decode JSON from {file_path}: {e}")
            return questions
        except Exception as e:
            logger.error(f"Unexpected error loading JSON file {file_path}: {e}")
            return questions

        if not isinstance(data, list):
            logger.error(f"Top-level structure of JSON must be a list, got {type(data).__name__}")
            return questions

        for idx, item in enumerate(data):
            try:
                if not isinstance(item, dict):
                    raise ValueError(f"Item is not a dictionary: {type(item).__name__}")
                
                # Extract and validate qid
                if "qid" not in item:
                    raise KeyError("Missing 'qid' field")
                qid = str(item["qid"]).strip()
                if not qid:
                    raise ValueError("Empty 'qid'")

                # Extract and validate question
                if "question" not in item:
                    raise KeyError("Missing 'question' field")
                question = str(item["question"]).strip()
                if not question:
                    raise ValueError("Empty 'question'")

                # Extract and validate choices
                if "choices" not in item:
                    raise KeyError("Missing 'choices' field")
                choices_raw = item["choices"]
                if not isinstance(choices_raw, list):
                    raise TypeError(f"Choices must be a list, got {type(choices_raw).__name__}")
                
                # Sanitize choices
                choices = [str(c).strip() for c in choices_raw]
                if len(choices) < 2:
                    raise ValueError(f"Invalid choices list length: {len(choices)}")

                questions.append({
                    "qid": qid,
                    "question": question,
                    "choices": choices
                })
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"[WARNING] Malformed JSON item at index {idx}: {e}. Skipping record.")
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error parsing JSON item at index {idx}: {e}. Skipping record.")

    elif ext == ".csv":
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read CSV from {file_path}: {e}")
            return questions
        except Exception as e:
            logger.error(f"Unexpected error loading CSV file {file_path}: {e}")
            return questions

        # Validate columns
        required_cols = {"qid", "question", "choices"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            logger.error(f"CSV file is missing required columns: {missing_cols}")
            return questions

        for idx, row in df.iterrows():
            try:
                # Handle potential NaN values
                if pd.isna(row["qid"]):
                    raise ValueError("Empty 'qid'")
                qid = str(row["qid"]).strip()
                if not qid:
                    raise ValueError("Empty 'qid'")

                if pd.isna(row["question"]):
                    raise ValueError("Empty 'question'")
                question = str(row["question"]).strip()
                if not question:
                    raise ValueError("Empty 'question'")

                choices_val = row["choices"]
                if pd.isna(choices_val):
                    raise ValueError("Empty 'choices'")

                choices = []
                if isinstance(choices_val, list):
                    choices = [str(c).strip() for c in choices_val]
                elif isinstance(choices_val, str):
                    # Try to parse string representation of list
                    choices_val_str = choices_val.strip()
                    try:
                        parsed = ast.literal_eval(choices_val_str)
                        if isinstance(parsed, list):
                            choices = [str(c).strip() for c in parsed]
                        else:
                            raise TypeError(f"Parsed choices is not a list: {type(parsed).__name__}")
                    except Exception as e:
                        raise ValueError(f"Failed to parse choices string as list: {e}")
                else:
                    raise TypeError(f"Unsupported choices type: {type(choices_val).__name__}")

                if len(choices) < 2:
                    raise ValueError(f"Invalid choices list length: {len(choices)}")

                questions.append({
                    "qid": qid,
                    "question": question,
                    "choices": choices
                })
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"[WARNING] Malformed CSV row at index {idx}: {e}. Skipping record.")
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error parsing CSV row at index {idx}: {e}. Skipping record.")

    else:
        logger.error(f"Unsupported file format: {ext}. Only .json and .csv are supported.")

    return questions
