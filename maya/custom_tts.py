#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""自定義 TTS 服務 - 避免中斷問題"""

from typing import AsyncGenerator

from loguru import logger
from pipecat.frames.frames import Frame, InterruptionFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService


class NonInterruptibleElevenLabsTTSService(ElevenLabsTTSService):
    """不可中斷的 ElevenLabs TTS 服務"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_speaking = False
    
    async def _handle_interruption(self, frame: InterruptionFrame, direction: FrameDirection):
        """忽略中斷信號，讓 TTS 完整播放"""
        if self._is_speaking:
            logger.debug("🔇 忽略中斷信號 - Maya 正在說話")
            return  # 不處理中斷
        else:
            # 如果不在說話，正常處理中斷
            await super()._handle_interruption(frame, direction)
    
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """運行 TTS，標記說話狀態"""
        self._is_speaking = True
        logger.debug("🎤 Maya 開始說話")
        
        try:
            async for frame in super().run_tts(text):
                yield frame
        finally:
            self._is_speaking = False
            logger.debug("🎤 Maya 說話結束")
