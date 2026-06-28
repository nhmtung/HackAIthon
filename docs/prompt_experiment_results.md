# 🧪 Prompt Engineering & CoT Experiment Results

Executed at: 2026-06-28 19:18:33
Base Model: `Qwen/Qwen2.5-3B-Instruct`
Gold Subset Size: 3 questions

## Summary Comparison Table

| Prompt Mode | Accuracy | Correct | Elapsed Time | Speed (Req/s) |
|---|---|---|---|---|
| `zero_shot` | 0.3333 | 1/3 | 0.00s | 1572864.00 |
| `few_shot` | 0.3333 | 1/3 | 0.00s | 1572864.00 |
| `cot` | 0.3333 | 1/3 | 0.00s | 1143901.09 |
| `routed` | 0.3333 | 1/3 | 0.00s | 3145728.00 |
| `mixed_lang` | 0.3333 | 1/3 | 0.00s | 6291456.00 |

## Detailed Per-Question Results

| QID | Mode | Question Preview | Ground Truth | Prediction | Correct? | Raw Output Snippet |
|---|---|---|---|---|---|---|
| test_0001 | `zero_shot` | Thủ đô của Việt Nam là gì?... | A | A | ✅ | `A...` |
| test_0002 | `zero_shot` | Đoạn thông tin: Mặt trời mọc ở hướng Đông và lặn ở hướng Tây... | B | A | ❌ | `A...` |
| test_0003 | `zero_shot` | Tính giá trị của biểu thức sau: $2 + 3 * 5$... | B | A | ❌ | `A...` |
| test_0001 | `few_shot` | Thủ đô của Việt Nam là gì?... | A | A | ✅ | `A...` |
| test_0002 | `few_shot` | Đoạn thông tin: Mặt trời mọc ở hướng Đông và lặn ở hướng Tây... | B | A | ❌ | `A...` |
| test_0003 | `few_shot` | Tính giá trị của biểu thức sau: $2 + 3 * 5$... | B | A | ❌ | `A...` |
| test_0001 | `cot` | Thủ đô của Việt Nam là gì?... | A | A | ✅ | `Suy nghĩ: 0. Do đó đáp án là A.\nĐáp án: A...` |
| test_0002 | `cot` | Đoạn thông tin: Mặt trời mọc ở hướng Đông và lặn ở hướng Tây... | B | A | ❌ | `Suy nghĩ: 1. Do đó đáp án là A.\nĐáp án: A...` |
| test_0003 | `cot` | Tính giá trị của biểu thức sau: $2 + 3 * 5$... | B | A | ❌ | `Suy nghĩ: 2. Do đó đáp án là A.\nĐáp án: A...` |
| test_0001 | `routed` | Thủ đô của Việt Nam là gì?... | A | A | ✅ | `A...` |
| test_0002 | `routed` | Đoạn thông tin: Mặt trời mọc ở hướng Đông và lặn ở hướng Tây... | B | A | ❌ | `A...` |
| test_0003 | `routed` | Tính giá trị của biểu thức sau: $2 + 3 * 5$... | B | A | ❌ | `A...` |
| test_0001 | `mixed_lang` | Thủ đô của Việt Nam là gì?... | A | A | ✅ | `A...` |
| test_0002 | `mixed_lang` | Đoạn thông tin: Mặt trời mọc ở hướng Đông và lặn ở hướng Tây... | B | A | ❌ | `A...` |
| test_0003 | `mixed_lang` | Tính giá trị của biểu thức sau: $2 + 3 * 5$... | B | A | ❌ | `A...` |
