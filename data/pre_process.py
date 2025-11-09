import pandas as pd
import json

# 配置部分，请根据您的实际情况修改
EXCEL_FILE_PATH = "/home/shengkun/LLaMA-Factory/data/original_data/风险管控措施清单01.xlsx"  # 替换为您的Excel文件路径
OUTPUT_JSON_FILE = "/home/shengkun/LLaMA-Factory/data/processed_data/risk_action_list.json"

# 定义Excel中的列名 (请根据您的实际列名调整)
COLUMN_NAMES = {
    'risk_analysis_object': '风险分析对象',        # 风险分析对象
    'major_hazard_level': '重大危险源级别',      # 重大危险源级别
    'risk_analysis_unit': '风险分析单元',        # 风险分析单元
    'risk_event': '风险事件-最严重事故后果',                    # 风险事件
    'control_category_1': '管控措施分类1',       # 管控措施分类1
    'control_category_2': '管控措施分类2',       # 管控措施分类2
    'control_category_3': '管控措施分类3',       # 管控措施分类3
    'specific_measures': '具体管控措施',         # 具体管控措施
    'hazard_inspection': '隐患排查内容'          # 隐患排查内容
}

def main():
    print(f"正在读取 Excel 文件: {EXCEL_FILE_PATH}")
    try:
        # 读取Excel文件
        df = pd.read_excel(EXCEL_FILE_PATH, dtype=str, skiprows=1, header=0)  # 强制转换为字符串，避免类型错误
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{EXCEL_FILE_PATH}'。请检查文件路径是否正确。")
        return
    except Exception as e:
        print(f"读取 Excel 文件时发生错误: {e}")
        return

    print(f"成功读取 {len(df)} 行数据。")

    # 存储所有样本的列表
    dataset = []

    # 遍历每一行数据
    for index, row in df.iterrows():
        # 构建 input 字段
        input_text = (
            f"风险分析对象: {row[COLUMN_NAMES['risk_analysis_object']]}\n"
            f"重大危险源级别: {row[COLUMN_NAMES['major_hazard_level']]}\n"
            f"风险分析单元: {row[COLUMN_NAMES['risk_analysis_unit']]}\n"
            f"风险事件: {row[COLUMN_NAMES['risk_event']]}"
        )

        # 构建 output 字段
        output_text = (
            f"管控措施分类1: {row[COLUMN_NAMES['control_category_1']]}\n"
            f"管控措施分类2: {row[COLUMN_NAMES['control_category_2']]}\n"
            f"管控措施分类3: {row[COLUMN_NAMES['control_category_3']]}\n"
            f"具体管控措施: {row[COLUMN_NAMES['specific_measures']]}\n"
            f"隐患排查内容: {row[COLUMN_NAMES['hazard_inspection']]}"
        )

        # 创建单个样本的字典
        sample = {
            "instruction": "根据提供的输入信息，生成管控措施分类1, 管控措施分类2, 管控措施分类3, 具体管控措施和隐患排查内容",
            "input": input_text,
            "output": output_text
        }

        dataset.append(sample)

    # 写入JSON文件
    try:
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 数据预处理完成！已成功生成 {OUTPUT_JSON_FILE} 文件，共包含 {len(dataset)} 条数据。")
    except Exception as e:
        print(f"写入 JSON 文件时发生错误: {e}")

if __name__ == "__main__":
    main()