#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 機器人核心邏輯模組

實現 Maya 語音聊天機器人的主要業務邏輯
"""

from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.filters.stt_mute_filter import STTMuteConfig, STTMuteFilter, STTMuteStrategy
from pipecat.runner.types import RunnerArguments
from pipecat.transports.base_transport import BaseTransport

from maya.config import MayaConfig
from maya.processors import MayaChatProcessor, MetricsLogger
from maya.services import ServiceFactory


async def run_maya_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """運行 Maya 機器人的核心邏輯"""
    logger.info("🎭 啟動 Maya 語音聊天機器人...")
    logger.info(f"🌏 語音辨識: {MayaConfig.STT_LANGUAGE}")
    logger.info("💡 開始說話進行對話...")

    # 創建服務實例
    stt = ServiceFactory.create_stt_service()
    tts = ServiceFactory.create_tts_service()

    # 創建處理器
    maya_processor = MayaChatProcessor()
    metrics_logger = MetricsLogger()

    # 創建 STT 靜音過濾器 - 防止機器人說話時被自己中斷
    stt_mute_filter = STTMuteFilter(
        config=STTMuteConfig(strategies={STTMuteStrategy.ALWAYS})
    )
    logger.info("🎙️ 已啟用 STT 靜音過濾器 - 機器人說話時會自動靜音 STT")

    # 創建Pipeline - 加入 STT 靜音過濾器防止中斷
    pipeline = Pipeline([
        transport.input(),      # 語音輸入
        stt_mute_filter,        # STT 靜音過濾器（機器人說話時靜音 STT）
        stt,                    # 語音轉文字
        maya_processor,         # Maya對話處理
        tts,                    # 文字轉語音
        metrics_logger,         # 度量記錄
        transport.output()      # 語音輸出
    ])

    # 創建任務 - 啟用度量功能
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=MayaConfig.ENABLE_METRICS,
            enable_usage_metrics=MayaConfig.ENABLE_USAGE_METRICS,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )

    # 設置 VAD 參數以避免語音中斷
    if hasattr(transport, 'vad_analyzer') and transport.vad_analyzer:
        transport.vad_analyzer.set_params(
            confidence=MayaConfig.VAD_CONFIDENCE,
            start_secs=MayaConfig.VAD_START_SECS,
            stop_secs=MayaConfig.VAD_STOP_SECS,
            min_volume=MayaConfig.VAD_MIN_VOLUME
        )
        logger.info(f"🎙️ VAD 參數已設置 - 信心度: {MayaConfig.VAD_CONFIDENCE}, 開始: {MayaConfig.VAD_START_SECS}s, 停止: {MayaConfig.VAD_STOP_SECS}s")

    # 事件處理器
    @transport.event_handler("on_client_connected")
    async def on_client_connected(_transport, _client):
        logger.info("🔗 客戶端已連接")
        # 可選：主動開始對話
        # await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport, _client):
        logger.info("🔌 客戶端已斷開連接")
        await task.cancel()

    # 創建運行器
    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    
    try:
        await runner.run(task)
    except KeyboardInterrupt:
        logger.info("👋 再見！Maya 已經結束對話，下次見！")
    except (RuntimeError, ConnectionError, OSError) as e:
        logger.error(f"❌ 運行錯誤: {e}")


async def bot(runner_args: RunnerArguments):
    """主要機器人入口點 - 符合 Pipecat Cloud 標準"""
    # 對於本地音頻，直接創建 LocalAudioTransport
    transport = ServiceFactory.create_local_transport()
    await run_maya_bot(transport, runner_args)
