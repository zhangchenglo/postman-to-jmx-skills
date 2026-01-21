#!/usr/bin/env python3
"""
Postman Collection to JMeter JMX Converter

Converts Postman collection JSON files to JMeter test plan JMX format.
Avoids common conversion errors:
- Empty intProp/boolProp elements
- Missing name attribute in elementProp
- Incorrect SampleSaveConfiguration format
"""

import json
import sys
import os
from pathlib import Path

# Template for JMX header/footer
JMX_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{test_name}" enabled="true">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" enabled="true">
        <collectionProp name="Arguments.arguments">
{user_variables}
        </collectionProp>
      </elementProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Defaults">
        <stringProp name="HTTPSampler.domain">{domain}</stringProp>
        <stringProp name="HTTPSampler.port">{port}</stringProp>
        <stringProp name="HTTPSampler.protocol">{protocol}</stringProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments"/>
        </elementProp>
        <stringProp name="HTTPSampler.implementation"></stringProp>
      </ConfigTestElement>
      <hashTree/>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <intProp name="ThreadGroup.num_threads">1</intProp>
        <intProp name="ThreadGroup.ramp_time">1</intProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController">
          <stringProp name="LoopController.loops">1</stringProp>
          <boolProp name="LoopController.continue_forever">false</boolProp>
        </elementProp>
      </ThreadGroup>
      <hashTree>
{samples}
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>false</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>false</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''

HTTPSAMPLER_TEMPLATE = '''        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{name}">
          <stringProp name="HTTPSampler.path">{path}</stringProp>
          <stringProp name="HTTPSampler.method">{method}</stringProp>
          <boolProp name="HTTPSampler.postBodyRaw">{post_body_raw}</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments"{guiclass_attr}>
            <collectionProp name="Arguments.arguments">
{arguments}
            </collectionProp>
          </elementProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <intProp name="Assertion.test_type">2</intProp>
            <stringProp name="Assertion.custom_message"></stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>'''

HTTPARGUMENT_TEMPLATE = '''              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{value}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>'''

VARIABLE_TEMPLATE = '''          <elementProp name="{var_name}" elementType="Argument">
            <stringProp name="Argument.name">{var_name}</stringProp>
            <stringProp name="Argument.value">{var_value}</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>'''


def escape_xml(text):
    """Escape special XML characters."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def format_json_body(body):
    """Format JSON body for JMeter, converting newlines properly."""
    if not body:
        return ""

    # Format JSON with proper indentation
    try:
        parsed = json.loads(body)
        formatted = json.dumps(parsed, indent=2)
        # Add carriage return and format for JMeter
        lines = formatted.split('\n')
        result = "&#xd;\n"
        for line in lines:
            result += '                    ' + line + '&#xd;\n'
        return result
    except json.JSONDecodeError:
        # If not valid JSON, escape as-is
        return "&#xd;\n" + escape_xml(body)


def parse_url(url_obj):
    """Parse Postman URL object to extract components."""
    raw = url_obj.get("raw", "")
    host = url_obj.get("host", [])
    path = url_obj.get("path", [])

    # Handle variable in host (e.g., "{{URL}}")
    if host and isinstance(host[0], str) and host[0].startswith("{{"):
        domain = ""
    elif host:
        domain = ".".join(host) if isinstance(host, list) else str(host)
    else:
        domain = ""

    # Build path
    if path:
        path_str = "/" + "/".join(path) if isinstance(path, list) else str(path)
    else:
        path_str = raw.split(host[0] if host and isinstance(host[0], str) else "")[-1] if host else raw

    # Extract protocol
    protocol = url_obj.get("protocol", "https")

    # Extract port
    port = str(url_obj.get("port", 443 if protocol == "https" else 80))

    return {
        "domain": domain,
        "path": path_str,
        "protocol": protocol,
        "port": port
    }


def parse_body(body_obj):
    """Parse Postman body object and return formatted arguments."""
    if not body_obj:
        return []

    mode = body_obj.get("mode", "")

    if mode == "raw":
        raw_data = body_obj.get("raw", "")
        # Check if it's JSON
        options = body_obj.get("options", {})
        lang = options.get("raw", {}).get("language", "")
        if lang == "json" or raw_data.strip().startswith("{") or raw_data.strip().startswith("["):
            return [{
                "value": format_json_body(raw_data),
                "post_body_raw": "true"
            }]
        else:
            return [{
                "value": escape_xml(raw_data),
                "post_body_raw": "true"
            }]

    elif mode == "formdata":
        args = []
        for item in body_obj.get("formdata", []):
            if not item.get("disabled", False):
                args.append({
                    "value": escape_xml(item.get("value", "")),
                    "post_body_raw": "false"
                })
        return args

    return []


def parse_postman_environment(env_path):
    """Parse Postman environment JSON file and return variables dict."""
    if not os.path.exists(env_path):
        return {}

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            env_data = json.load(f)

        variables = {}
        for value in env_data.get("values", []):
            key = value.get("key", "")
            val = value.get("value", "")
            enabled = value.get("enabled", True)

            if key and enabled:
                variables[key] = val

        return variables
    except Exception as e:
        print(f"Warning: Could not parse environment file: {e}")
        return {}


def format_variables_section(variables):
    """Format user-defined variables section for JMeter."""
    if not variables:
        return "          <!-- Add user-defined variables here -->"

    lines = []
    for key, value in variables.items():
        lines.append(VARIABLE_TEMPLATE.format(
            var_name=escape_xml(key),
            var_value=escape_xml(str(value))
        ))
    return "\n".join(lines)


def convert_collection(collection_path, output_path=None, environment_path=None):
    """Convert Postman collection to JMX format."""
    # Read collection
    with open(collection_path, 'r', encoding='utf-8') as f:
        collection = json.load(f)

    info = collection.get("info", {})
    test_name = info.get("name", "Postman Collection")

    items = collection.get("item", [])

    # Read environment variables
    env_variables = {}
    if environment_path and os.path.exists(environment_path):
        env_variables = parse_postman_environment(environment_path)
        print(f"Loaded environment variables from: {environment_path}")
        for key, value in env_variables.items():
            print(f"  {key} = {value}")
    elif environment_path:
        print(f"Environment file not found: {environment_path}")

    # Initialize variables
    samples = []
    domain = ""
    port = ""
    protocol = ""

    for item in items:
        item_request = item.get("request", {})
        item_name = item.get("name", "Request")

        # Get URL
        url = item_request.get("url", {})
        if isinstance(url, str):
            url = {"raw": url}
        url_parts = parse_url(url)

        # Update domain/protocol if first request sets them
        if not domain and url_parts["domain"]:
            domain = url_parts["domain"]
            port = url_parts["port"]
            protocol = url_parts["protocol"]

        # Get method
        method = item_request.get("method", "GET")

        # Get body
        body = item_request.get("body", {})
        arguments = parse_body(body)

        if arguments:
            args_xml = ""
            for arg in arguments:
                args_xml += HTTPARGUMENT_TEMPLATE.format(value=arg["value"])
            post_body_raw = arguments[0]["post_body_raw"]
            guiclass_attr = ""
        else:
            args_xml = ""
            post_body_raw = "false"
            guiclass_attr = ' guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables"'

        # Build HTTPSampler
        sample = HTTPSAMPLER_TEMPLATE.format(
            name=item_name,
            path=escape_xml(url_parts["path"]),
            method=method,
            post_body_raw=post_body_raw,
            guiclass_attr=guiclass_attr,
            arguments=args_xml
        )
        samples.append(sample)

    # Generate user variables section from environment
    user_variables = format_variables_section(env_variables)

    # Build final JMX
    jmx_content = JMX_TEMPLATE.format(
        test_name=test_name,
        user_variables=user_variables,
        domain=escape_xml(domain),
        port=escape_xml(port),
        protocol=escape_xml(protocol),
        samples="\n".join(samples)
    )

    # Write output
    if not output_path:
        output_path = collection_path.replace(".json", ".jmx")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(jmx_content)

    print(f"Converted: {collection_path} -> {output_path}")
    return output_path


def interactive_mode():
    """Interactive mode: prompt user for inputs."""
    import getpass

    print("\n=== Postman to JMeter Converter (Interactive Mode) ===\n")

    # Ask for collection file
    collection_path = input("Postman Collection JSON 文件路径: ").strip()
    if not collection_path:
        print("错误: 必须提供 collection 文件路径")
        return None

    if not os.path.exists(collection_path):
        print(f"错误: 文件不存在: {collection_path}")
        return None

    # Ask for output path
    output_path = input("输出 JMX 文件路径 (直接回车使用默认路径): ").strip()
    if not output_path:
        output_path = collection_path.replace(".json", ".jmx")

    # Ask for environment file
    print("\n是否需要导入 Postman 环境变量文件?")
    print("  1) 否 - 跳过环境变量")
    print("  2) 是 - 指定环境变量文件")
    choice = input("请选择 [1/2]: ").strip()

    environment_path = None
    if choice == "2":
        environment_path = input("Postman Environment JSON 文件路径: ").strip()
        if not environment_path:
            print("警告: 未提供环境变量文件路径，跳过环境变量")
            environment_path = None
        elif not os.path.exists(environment_path):
            print(f"警告: 环境变量文件不存在: {environment_path}，跳过环境变量")
            environment_path = None

    return {
        "collection": collection_path,
        "output": output_path,
        "environment": environment_path
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Interactive mode
        result = interactive_mode()
        if result is None:
            sys.exit(1)

        convert_collection(
            result["collection"],
            result["output"],
            result["environment"]
        )
    else:
        collection_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        environment_path = sys.argv[3] if len(sys.argv) > 3 else None

        convert_collection(collection_path, output_path, environment_path)
