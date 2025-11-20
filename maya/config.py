#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 配置模組

管理所有配置參數、環境變數和常數設定
"""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from pipecat.transcriptions.language import Language

# 載入環境變數
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Maya 基本配置
class MayaConfig:
    """Maya 聊天機器人配置類"""
    
    # 語言設定
    STT_LANGUAGE = os.getenv("MAYA_STT_LANG", "zh-TW")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    
    # 服務配置
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_STT_MODEL = "gpt-4o-transcribe"
    ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Bella 語音 (年輕女性)
    
    # VAD 配置 - 嚴格避免語音中斷
    VAD_CONFIDENCE = 0.95     # 非常高的信心度
    VAD_START_SECS = 2.0      # 需要說話 2 秒才觸發
    VAD_STOP_SECS = 3.0       # 停止說話 3 秒後才結束
    VAD_MIN_VOLUME = 0.9      # 很高的音量門檻
    
    # Pipeline 配置
    ENABLE_METRICS = True
    ENABLE_USAGE_METRICS = True
    PIPELINE_IDLE_TIMEOUT_SECS = 300
    
    # 對話配置
    MAX_CONVERSATION_HISTORY = 7  # system prompt + 6輪對話
    
    # 系統提示詞
    SYSTEM_PROMPT = (
        "你是Maya，一個友善的AI助手。你擅長用中文對話，會用自然、親切的語氣回應用戶。"
        "當用戶用中文說話時，你也用中文回應。你的個性溫暖、樂於助人，總是用正面的態度面對每一個問題。"
    )
    
    @classmethod
    def get_language_mapping(cls) -> Dict[str, Language]:
        """獲取語言映射"""
        return {
            "zh-TW": Language.ZH_TW,
            "zh": Language.ZH,
            "zh-HK": Language.ZH_HK,
            "en": Language.EN,
        }
    
    @classmethod
    def get_selected_language(cls) -> Language:
        """根據環境變數獲取選定的語言"""
        language_map = cls.get_language_mapping()
        return language_map.get(cls.STT_LANGUAGE, Language.ZH_TW)
    
    @classmethod
    def validate_api_keys(cls) -> Optional[list]:
        """驗證必要的 API Keys"""
        required_keys = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "ELEVENLABS_API_KEY": cls.ELEVENLABS_API_KEY,
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        return missing_keys if missing_keys else None
