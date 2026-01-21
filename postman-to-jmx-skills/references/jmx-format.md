# JMX Template Reference

This file contains the standard JMX template structure used by the converter.

## Correct ElementProp Format

### HTTPSamplerProxy with raw body (POST/PUT)
```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Request Name">
  <stringProp name="HTTPSampler.path">/api/endpoint</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
    <collectionProp name="Arguments.arguments">
      <elementProp name="" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">&#xd;
{
    "key": "value"
}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
</HTTPSamplerProxy>
```

### HTTPSamplerProxy with form data (no body)
```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Request Name">
  <stringProp name="HTTPSampler.path">/api/endpoint</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
  <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
</HTTPSamplerProxy>
```

## Common Mistakes to Avoid

### Wrong: Empty boolProp/intProp
```xml
<intProp name="ThreadGroup.ramp_time"/>     <!-- ERROR: no value -->
```

### Correct: With value
```xml
<intProp name="ThreadGroup.ramp_time">1</intProp>   <!-- OK -->
```

### Wrong: Missing name attribute
```xml
<elementProp elementType="HTTPArgument">           <!-- ERROR: missing name -->
```

### Correct: With name attribute
```xml
<elementProp name="" elementType="HTTPArgument">   <!-- OK -->
```

### Wrong: SampleSaveConfiguration format
```xml
<value class="SampleSaveConfiguration">
  <boolProp name="SampleSaveConfiguration.time"/>   <!-- ERROR -->
</value>
```

### Correct: Direct element format
```xml
<value class="SampleSaveConfiguration">
  <time>true</time>                                 <!-- OK -->
</value>
```

## Response Assertion
```xml
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion">
  <collectionProp name="Asserion.test_strings">
    <stringProp name="49586">200</stringProp>
  </collectionProp>
  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
  <intProp name="Assertion.test_type">2</intProp>
  <stringProp name="Assertion.custom_message"></stringProp>
  <boolProp name="Assertion.assume_success">false</boolProp>
</ResponseAssertion>
```

## Result Collector (View Results Tree)
```xml
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
```
