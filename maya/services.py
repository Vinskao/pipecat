#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 服務工廠模組

負責創建和配置各種 AI 服務
"""

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from maya.config import MayaConfig
from maya.custom_tts import NonInterruptibleElevenLabsTTSService


class ServiceFactory:
    """服務工廠類 - 負責創建各種 AI 服務實例"""
    
    @staticmethod
    def create_stt_service() -> OpenAISTTService:
        """創建語音轉文字服務"""
        return OpenAISTTService(
            api_key=MayaConfig.OPENAI_API_KEY,
            model=MayaConfig.OPENAI_STT_MODEL,
            language=MayaConfig.get_selected_language()
        )
    
    @staticmethod
    def create_tts_service() -> NonInterruptibleElevenLabsTTSService:
        """創建文字轉語音服務（不可中斷版本）"""
        return NonInterruptibleElevenLabsTTSService(
            api_key=MayaConfig.ELEVENLABS_API_KEY,
            voice_id=MayaConfig.ELEVENLABS_VOICE_ID
        )
    
    @staticmethod
    def create_vad_analyzer() -> SileroVADAnalyzer:
        """創建語音活動檢測器"""
        # SileroVADAnalyzer 參數通過 set_params 方法設置
        analyzer = SileroVADAnalyzer()
        # 參數會在 transport 初始化時自動設置
        return analyzer
    
    @staticmethod
    def create_local_transport() -> LocalAudioTransport:
        """創建本地音頻傳輸"""
        transport = LocalAudioTransport(
            LocalAudioTransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=ServiceFactory.create_vad_analyzer()
            )
        )
        # 嘗試禁用中斷機制
        if hasattr(transport, '_enable_interruptions'):
            transport._enable_interruptions = False
        return transport


# 傳輸參數配置 - 支援多種傳輸方式
def create_local_transport_params():
    """創建本地音頻傳輸參數"""
    vad_analyzer = SileroVADAnalyzer()
    # VAD 參數將在 transport 初始化後通過 set_params 方法設置

    return LocalAudioTransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=vad_analyzer
    )

transport_params = {
    "local": create_local_transport_params,
}
