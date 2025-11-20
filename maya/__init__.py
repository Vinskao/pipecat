#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 語音聊天機器人

一個基於 Pipecat 框架的智能語音對話系統，支援：
- 台灣中文語音辨識 (OpenAI STT)
- GPT-4o-mini 對話生成
- ElevenLabs 語音合成
- 實時性能監控
- 可配置的語音活動檢測
"""

from maya.bot import bot, run_maya_bot
from maya.config import MayaConfig
from maya.processors import MayaChatProcessor, MetricsLogger
from maya.services import ServiceFactory, transport_params

__version__ = "1.0.0"
__author__ = "Maya Team"

__all__ = [
    "bot",
    "run_maya_bot", 
    "MayaConfig",
    "MayaChatProcessor",
    "MetricsLogger",
    "ServiceFactory",
    "transport_params",
]
