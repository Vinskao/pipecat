#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 自定義處理器模組

包含 Maya 特有的 FrameProcessor 實現
"""

from loguru import logger
from pipecat.frames.frames import Frame, MetricsFrame, TTSSpeakFrame, TranscriptionFrame
from pipecat.metrics.metrics import (
    LLMUsageMetricsData,
    ProcessingMetricsData,
    TTFBMetricsData,
    TTSUsageMetricsData,
)
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.openai.llm import OpenAILLMService

from maya.config import MayaConfig


class MetricsLogger(FrameProcessor):
    """度量記錄器 - 監控系統性能"""
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, MetricsFrame):
            for d in frame.data:
                if isinstance(d, TTFBMetricsData):
                    logger.info(f"🚀 首字節時間: {d.value:.2f}ms")
                elif isinstance(d, ProcessingMetricsData):
                    logger.info(f"⚡ 處理時間: {d.value:.2f}ms")
                elif isinstance(d, LLMUsageMetricsData):
                    tokens = d.value
                    logger.info(f"🧠 LLM使用: 輸入{tokens.prompt_tokens}tokens, 輸出{tokens.completion_tokens}tokens")
                elif isinstance(d, TTSUsageMetricsData):
                    logger.info(f"🔊 TTS字符數: {d.value}")
        
        await self.push_frame(frame, direction)


class MayaChatProcessor(FrameProcessor):
    """Maya 專屬的對話處理器"""

    def __init__(self):
        super().__init__()
        self.conversation_history = [
            {"role": "system", "content": MayaConfig.SYSTEM_PROMPT}
        ]
        self.llm = OpenAILLMService(
            model=MayaConfig.OPENAI_MODEL,
            api_key=MayaConfig.OPENAI_API_KEY
        )
    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # 處理語音轉文字結果
        if isinstance(frame, TranscriptionFrame):
            user_text = frame.text.strip()
            if user_text:
                logger.info(f"👤 用戶說話: {user_text}")

                # 添加用戶訊息到對話歷史
                self.conversation_history.append({"role": "user", "content": user_text})

                # 限制對話歷史長度
                if len(self.conversation_history) > MayaConfig.MAX_CONVERSATION_HISTORY:
                    self.conversation_history = [
                        self.conversation_history[0]
                    ] + self.conversation_history[-6:]

                # 創建LLM上下文
                context = OpenAILLMContext(self.conversation_history)

                # 獲取AI回應
                try:
                    ai_response = await self.llm.run_inference(context)
                    ai_text = ai_response.strip()
                    logger.info(f"🤖 Maya回應: {ai_text}")

                    # 添加AI回應到對話歷史
                    self.conversation_history.append({"role": "assistant", "content": ai_text})

                    # 發送語音輸出
                    await self.push_frame(TTSSpeakFrame(ai_text))

                except (ValueError, RuntimeError, ConnectionError) as e:
                    logger.error(f"❌ LLM錯誤: {e}")
                    error_msg = "抱歉，我遇到了一些問題，請再試一次。"
                    await self.push_frame(TTSSpeakFrame(error_msg))

        # 繼續傳遞幀
        await self.push_frame(frame, direction)
