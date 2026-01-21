# postman-to-jmx-skills

A Claude Code skill that converts Postman collection JSON files to Apache JMeter JMX test plans.

## Overview

This skill converts API collections exported from Postman into Apache JMeter load test scripts. It supports common HTTP methods (GET, POST, PUT, DELETE, PATCH) with JSON body and form data, preserving Postman variables and adding response assertions.

## Demo Video

Check out the [demo video](template/postman-to-jmx.mp4) to see how this skill works:

<video src="template/postman-to-jmx.mp4" width="100%" controls>
  Your browser does not support the video tag. <a href="template/postman-to-jmx.mp4">Download Video</a>
</video>

## Directory Structure

```
postman-to-jmx-skills/
├── README.md              # This file
├── SKILL.md               # Main skill documentation
├── scripts/
│   └── postman_to_jmx.py  # Python converter script
└── references/
    └── jmx-format.md      # JMeter JMX format reference
```

## Usage

### Interactive Mode (Recommended)

Run without arguments to enter interactive mode:

```bash
./postman-to-jmx-skills/scripts/postman_to_jmx.py
```

Interactive mode will prompt you for:
1. Postman Collection JSON file path
2. Output JMX file path (optional, defaults to same directory)
3. Environment variables file path (optional)

### Command Line Mode

Pass arguments directly:

```bash
./postman-to-jmx-skills/scripts/postman_to_jmx.py <collection.json> [output.jmx] [environment.json]
```

Examples:
```bash
# Basic conversion
./postman-to-jmx-skills/scripts/postman_to_jmx.py my-collection.json

# Specify output path
./postman-to-jmx-skills/scripts/postman_to_jmx.py my-collection.json my-test-plan.jmx

# With environment variables
./postman-to-jmx-skills/scripts/postman_to_jmx.py my-collection.json my-test-plan.jmx my-environment.json
```

## What This Skill Does

1. Parses Postman collection JSON files
2. Extracts requests (GET, POST, PUT, DELETE, PATCH)
3. Converts to valid JMeter JMX format with:
   - TestPlan with user-defined variables
   - HTTP Defaults configuration
   - Thread Group with proper loop settings
   - HTTPSamplerProxy for each request
   - Response Assertion for status code validation
   - View Results Tree listener

## Supported Features

- **HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **Body Types**: JSON raw, form-data
- **Response Assertions**: 200 status code check
- **Variables**: Postman variables (`{{variable}}`) preserved

## Limitations

- Does not convert Postman test scripts
- Does not convert authentication configurations
- Does not convert pre-request scripts
- File uploads not supported

## Import to Claude Code

There are two ways to import this skill:

### Option 1: Clone and Link (Recommended)

Clone this repository and link the skill to your Claude Code skills directory:

```bash
# Clone this repository
git clone https://github.com/yourusername/postman-to-jmx-skills.git
cd postman-to-jmx-skills

# Create a symlink in Claude Code skills directory
ln -sf "$(pwd)/postman-to-jmx-skills" ~/.claude/skills/postman-to-jmx-skills
```

### Option 2: Copy Directly

Copy the entire `postman-to-jmx-skills` folder to your Claude Code skills directory:

```bash
# Clone or download this repository
git clone https://github.com/yourusername/postman-to-jmx-skills.git

# Copy to Claude Code skills directory
cp -r postman-to-jmx-skills ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/postman-to-jmx-skills
```

After importing, the skill will be available for use with Claude Code. You can invoke it using the skill name `postman-to-jmx`.

## Output

Generates a `.jmx` file that can be opened directly in Apache JMeter.

## Common Conversion Issues Fixed

This skill avoids these common JMeter errors:

| Issue | Cause | Fix |
|-------|-------|-----|
| `NumberFormatException` | Empty `<intProp>` or `<boolProp>` tags | Always include values in prop tags |
| `MissingFieldException` | Incorrect `SampleSaveConfiguration` format | Use `<time>true</time>` not `<boolProp name="SampleSaveConfiguration.time"/>` |
| `ClassCastException` | Missing `name=""` attribute in `elementProp` | Always include `name=""` for HTTPArgument elements |
