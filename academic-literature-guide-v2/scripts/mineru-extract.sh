#!/bin/bash
# MinerU 自动化 PDF 提取脚本 (macOS/Linux)
# 用法：./mineru-extract.sh -i "path/to/file.pdf" [-o "./mineru_extract/output"] [-f]

set -e

# 默认参数
INPUT_PATH=""
OUTPUT_DIR=""
FORCE_EXTRACT=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_PATH="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--force-extract)
            FORCE_EXTRACT=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 -i <input_pdf> [-o <output_dir>] [-f]"
            echo "  -i, --input        PDF 文件路径（必需）"
            echo "  -o, --output       输出目录（可选，默认自动生成）"
            echo "  -f, --force-extract 强制使用 extract 模式"
            echo "  -h, --help         显示帮助"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [[ -z "$INPUT_PATH" ]]; then
    echo "✗ 错误：必须指定输入文件 (-i)"
    echo "用法: $0 -i <input_pdf> [-o <output_dir>] [-f]"
    exit 1
fi

# 检查 MinerU 是否安装
echo "正在检查 MinerU 安装..."
if ! command -v mineru-open-api &> /dev/null; then
    echo "✗ MinerU 未安装！"
    echo "请运行以下命令安装："
    echo "  npm install -g mineru-open-api"
    exit 1
fi

MINERU_VERSION=$(mineru-open-api version 2>&1 || echo "unknown")
echo "✓ MinerU 已安装：$MINERU_VERSION"

# 检查输入文件是否存在
if [[ ! -f "$INPUT_PATH" ]]; then
    echo "✗ 文件不存在：$INPUT_PATH"
    exit 1
fi

# 获取文件信息
FILE_NAME=$(basename "$INPUT_PATH")
FILE_SIZE_MB=$(du -m "$INPUT_PATH" | cut -f1)
echo "文件信息："
echo "  名称：$FILE_NAME"
echo "  大小：${FILE_SIZE_MB} MB"

# 自动选择提取模式
USE_EXTRACT=false
if [[ "$FORCE_EXTRACT" == true ]]; then
    USE_EXTRACT=true
    echo "→ 强制使用 extract 模式（用户指定）"
elif [[ $FILE_SIZE_MB -gt 10 ]]; then
    USE_EXTRACT=true
    echo "→ 文件超过 10MB，使用 extract 模式"
else
    echo "→ 使用 flash-extract 模式（快速）"
fi

# 生成输出目录
if [[ -z "$OUTPUT_DIR" ]]; then
    # 清理文件名中的特殊字符
    SAFE_NAME=$(echo "${FILE_NAME%.*}" | sed 's/[^a-zA-Z0-9_\u4e00-\u9fa5-]/_/g' | sed 's/__*/_/g')
    
    # 生成 MD5 hash（前 6 位）
    if command -v md5sum &> /dev/null; then
        HASH=$(echo -n "$(realpath "$INPUT_PATH")" | md5sum | cut -c1-6)
    elif command -v md5 &> /dev/null; then
        HASH=$(echo -n "$(realpath "$INPUT_PATH")" | md5 | cut -c1-6)
    else
        HASH=$(date +%s | cut -c1-6)
    fi
    
    OUTPUT_DIR="./mineru_extract/${SAFE_NAME}_${HASH}"
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
echo "✓ 创建输出目录：$OUTPUT_DIR"

# 执行提取
echo ""
echo "开始提取..."
if [[ "$USE_EXTRACT" == true ]]; then
    echo "命令：mineru-open-api extract \"$INPUT_PATH\" -o \"$OUTPUT_DIR\" --verbose"
    mineru-open-api extract "$INPUT_PATH" -o "$OUTPUT_DIR" --verbose
else
    echo "命令：mineru-open-api flash-extract \"$INPUT_PATH\" -o \"$OUTPUT_DIR\" --verbose"
    mineru-open-api flash-extract "$INPUT_PATH" -o "$OUTPUT_DIR" --verbose
fi

# 检查提取结果
if [[ $? -eq 0 ]]; then
    echo ""
    echo "✓ 提取成功！"
    
    # 列出生成的文件
    echo "输出文件："
    ls -la "$OUTPUT_DIR" | while read -r line; do
        if [[ $line == d* ]]; then
            echo "  📁 $(echo "$line" | awk '{print $NF}')"
        elif [[ $line == -* ]]; then
            SIZE_KB=$(echo "$line" | awk '{print $5}')
            SIZE_KB=$((SIZE_KB / 1024))
            echo "  📄 $(echo "$line" | awk '{print $NF}') (${SIZE_KB} KB)"
        fi
    done
    
    echo ""
    echo "输出目录：$OUTPUT_DIR"
else
    echo ""
    echo "✗ 提取失败！请检查错误信息。"
    echo "可能的原因："
    echo "  1. 文件加密或损坏"
    echo "  2. MinerU API 配额用尽"
    echo "  3. 网络连接问题"
    echo "尝试解决方案："
    echo "  - 检查文件是否可以正常打开"
    echo "  - 等待几分钟后重试"
    echo "  - 检查 MinerU Token 是否有效（运行：mineru-open-api auth --verify）"
    exit 1
fi
