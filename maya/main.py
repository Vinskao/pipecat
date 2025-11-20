#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Maya 語音聊天機器人主程序

符合 Pipecat 標準開發模式的入口點
支援本地音頻模式和 Web 模式
"""

import asyncio
import sys
from pathlib import Path

from loguru import logger
from pipecat.runner.types import RunnerArguments

# 添加父目錄到 Python 路徑以支持模組導入
sys.path.insert(0, str(Path(__file__).parent.parent))

from maya import bot
from maya.config import MayaConfig


async def main_local():
    """直接運行本地音頻版本的 Maya"""
    # 檢查必要的環境變數
    missing_vars = MayaConfig.validate_api_keys()
    if missing_vars:
        logger.error("❌ 缺少必要的環境變數:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("\n請檢查父目錄的 .env 文件是否正確設置")
        exit(1)

    logger.success("✅ 環境變數檢查通過")
    logger.info("🎭 Maya 已準備就緒...")
    
    # 創建 RunnerArguments 用於本地音頻
    runner_args = RunnerArguments()
    runner_args.handle_sigint = True
    runner_args.pipeline_idle_timeout_secs = MayaConfig.PIPELINE_IDLE_TIMEOUT_SECS
    
    # 直接運行本地音頻機器人
    await bot(runner_args)


def main():
    """主入口點"""
    # 檢查命令行參數，決定運行模式
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        # Web 模式：使用標準 Pipecat runner
        logger.info("🌐 啟動 Web 模式 (http://localhost:7860)")
        from pipecat.runner.run import main as pipecat_main
        pipecat_main()
    else:
        # 本地模式：直接運行本地音頻
        logger.info("🎤 啟動本地音頻模式")
        asyncio.run(main_local())


if __name__ == "__main__":
    main()