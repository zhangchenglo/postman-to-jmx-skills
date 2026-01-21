---
name: postman-to-jmeter
description: Converts Postman collection JSON files to Apache JMeter JMX test plans. Use when converting API collections exported from Postman to JMeter load test scripts. Supports GET, POST, PUT, DELETE methods with JSON body, form data, and response assertions.
---

# Postman to JMeter Converter

## Usage

### Interactive Mode (Recommended)
直接运行 skill，不带参数时会进入交互式模式：

```bash
~/.claude/skills/postman-to-jmeter/scripts/postman_to_jmx.py
```

交互式模式会提示：
1. 输入 Postman Collection JSON 文件路径
2. 输入输出 JMX 文件路径（可选，默认同目录）
3. 是否需要导入环境变量

### Command Line Mode
也可以直接传入参数：

```bash
~/.claude/skills/postman-to-jmeter/scripts/postman_to_jmx.py <collection.json> [output.jmx] [environment.json]
```

Examples:
```bash
# 纯转换，无环境变量
~/.claude/skills/postman-to-jmeter/scripts/postman_to_jmx.py my-collection.json

# 指定输出路径
~/.claude/skills/postman-to-jmeter/scripts/postman_to_jmx.py my-collection.json my-test-plan.jmx

# 包含环境变量
~/.claude/skills/postman-to-jmeter/scripts/postman_to_jmx.py my-collection.json my-test-plan.jmx my-environment.json
```

## What This Skill Does

1. Parses Postman collection JSON files
2. Extracts requests (GET, POST, PUT, DELETE)
3. Converts to valid JMeter JMX format with:
   - TestPlan with user-defined variables
   - HTTP Defaults configuration
   - Thread Group with proper loop settings
   - HTTPSamplerProxy for each request
   - Response Assertion for status code validation
   - View Results Tree listener

## Common Conversion Issues Fixed

This skill avoids these common errors:

| Issue | Cause | Fix |
|-------|-------|-----|
| `NumberFormatException: For input string: ""` | Empty `<intProp>` or `<boolProp>` tags | Always include values in prop tags |
| `MissingFieldException: Field not found` | Incorrect `SampleSaveConfiguration` format | Use `<time>true</time>` not `<boolProp name="SampleSaveConfiguration.time"/>` |
| `ClassCastException: ConfigTestElement cannot cast to HTTPArgument` | Missing `name=""` attribute in `elementProp` | Always include `name=""` for HTTPArgument elements |

## Supported Features

- **HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **Body Types**: JSON raw, form-data
- **Response Assertions**: 200 status code check
- **Variables**: Postman variables ({{variable}}) preserved

## Limitations

- Does not convert Postman test scripts
- Does not convert authentication configurations
- Does not convert pre-request scripts
- File uploads not supported

## Output

Generates a `.jmx` file that can be opened directly in Apache JMeter.
