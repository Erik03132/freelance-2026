# notebooklm-mcp · PyPI

Источник: https://pypi.org/project/notebooklm-mcp/

notebooklm-mcp · PyPI 

 Skip to main content 
 Switch to mobile version 

 Warning 

 Some features may not work without JavaScript. Please try enabling it if you encounter problems. 

 Search PyPI 
 search-focus#focusSearchField"
 data-search-focus-target="searchField">

 Search 

 Help 

 Docs 

 Sponsors 

 Log in 

 Register 

Menu 

 Help 

 Docs 

 Sponsors 

 Log in 

 Register 

 Search PyPI 

 Search 

 notebooklm-mcp 2.0.11

 FastMCP v2 server for NotebookLM automation with modern async support

 pip install notebooklm-mcp 

 Copy PIP instructions 

 project-tabs#tabKeydown"
 aria-label="Project description. Focus will be moved to the description.">

Description 

 project-tabs#tabKeydown"
 aria-label="Files. Focus will be moved to the project files.">

Download files 

 project-tabs#tabKeydown"
 aria-label="Release history. Focus will be moved to the release history panel.">

Release history 

 🚀 NotebookLM MCP

 Professional MCP server for Google NotebookLM automation • Available on PyPI • Production Ready 

 ✨ Key Features

 🔥 FastMCP v2 : Modern decorator-based MCP framework

 ⚡ UV Python Manager : Lightning-fast dependency management

 🚀 Multiple Transports : STDIO, HTTP, SSE support

 🎯 Type Safety : Full Pydantic validation

 🔒 Persistent Auth : Automatic Google session management

 📊 Rich CLI : Beautiful terminal interface with Taskfile automation

 🐳 Production Ready : Docker support with monitoring

 🏃‍♂️ Quick Start

 🎯 For End Users (Recommended)

 # Install UV (modern Python package manager) 
curl -LsSf https://astral.sh/uv/install.sh | sh

 # Install NotebookLM MCP from PyPI 
uv add notebooklm-mcp

 # Initialize with your NotebookLM URL 
uv run notebooklm-mcp init https://notebooklm.google.com/notebook/YOUR_NOTEBOOK_ID

 What happens after init : 

 ✅ Creates notebooklm-config.json with your settings

 ✅ Creates chrome_profile_notebooklm/ folder for persistent authentication

 ✅ Opens browser for one-time Google login (if needed)

 ✅ Saves session for future headless operation

 # Start server (STDIO for MCP clients) 
uv run notebooklm-mcp --config notebooklm-config.json server

 # Start HTTP server for web testing 
uv run notebooklm-mcp --config notebooklm-config.json server --transport http --port 8001 

 # Interactive chat mode 
uv run notebooklm-mcp --config notebooklm-config.json chat --message "Who are you ?" 

 👨‍💻 For Developers

 If you're contributing to this project, check out our Taskfile for enhanced developer experience:

 git clone https://github.com/khengyun/notebooklm-mcp.git
 cd notebooklm-mcp

 # Complete setup with development tools 
task setup

 # Show all available development tasks 
task --list

 🔧 Alternative Installation

 If you prefer pip over UV:

 # Install with pip 
pip install notebooklm-mcp

 # Initialize 
notebooklm-mcp init https://notebooklm.google.com/notebook/YOUR_NOTEBOOK_ID

 # Start server 
notebooklm-mcp --config notebooklm-config.json server

 � Project Structure After Init

 After running init , your working directory will contain:

 your-project/
├── notebooklm-config.json # Configuration file
├── chrome_profile_notebooklm/ # Browser profile (persistent auth)
│ ├── Default/ # Chrome profile data
│ ├── SingletonSocket # Session files
│ └── ... # Other Chrome data
└── your-other-files

 Key files: 

 notebooklm-config.json : Contains notebook ID, server settings, auth configuration

 chrome_profile_notebooklm/ : Stores Google authentication session (enables headless operation)

 �🛠️ Available Tools

 Tool 
 Description 
 Parameters 

 healthcheck 
 Server health status 
 None 

 send_chat_message 
 Send message to NotebookLM 
 message: str , wait_for_response: bool 

 get_chat_response 
 Get response with timeout 
 timeout: int 

 chat_with_notebook 
 Complete interaction 
 message: str , notebook_id?: str 

 navigate_to_notebook 
 Switch notebooks 
 notebook_id: str 

 get_default_notebook 
 Current notebook 
 None 

 set_default_notebook 
 Set default 
 notebook_id: str 

 get_quick_response 
 Instant response 
 None 

 👨‍💻 Developer Workflow

 For contributors and advanced users who want enhanced productivity, we provide a comprehensive Taskfile with 20+ automation tasks:

 # 📦 Dependency Management 
task deps-add -- requests # Add dependency 
task deps-add-dev -- pytest # Add dev dependency 
task deps-remove -- requests # Remove dependency 
task deps-list # List dependencies 
task deps-update # Update all dependencies 

 # 🧪 Testing &amp; Quality 
task test # Run all tests 
task test-quick # Quick validation test 
task test-coverage # Coverage analysis 
task enforce-test # MANDATORY after function changes 
task lint # Run all linting 
task format # Format code (Black + isort + Ruff) 

 # 🏗️ Build &amp; Release 
task build # Build package 
task clean # Clean artifacts 

 # 🚀 Server Commands 
task server-stdio # STDIO server 
task server-http # HTTP server 
task server-sse # SSE server 

 # Show all available tasks 
task --list

 💡 Pro Tip : Install Task for the best developer experience: go install github.com/go-task/task/v3/cmd/task@latest 

 🌐 Transport Options

 STDIO (Default)

 task server-stdio
 # For: LangGraph, CrewAI, AutoGen 

 HTTP

 task server-http 
 # Access: http://localhost:8001/mcp 
 # For: Web testing, REST APIs 

 SSE

 task server-sse
 # Access: http://localhost:8002/ 
 # For: Real-time streaming 

 🧪 Testing &amp; Development

 HTTP Client Testing

 from fastmcp import Client 
 from fastmcp.client.transports import StreamableHttpTransport 

 transport = StreamableHttpTransport ( url = "http://localhost:8001/mcp" ) 
 async with Client ( transport ) as client : 
 tools = await client . list_tools () 
 result = await client . call_tool ( "healthcheck" , {}) 

 Command Line Testing

 # Test with curl 
curl -X POST http://localhost:8001/mcp \ 
 -H "Content-Type: application/json" \ 
 -H "Accept: application/json, text/event-stream" \ 
 -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' 

 📊 Client Integration

 LangGraph

 from fastmcp import Client 
 from fastmcp.client.transports import StreamableHttpTransport 

 # HTTP transport 
 transport = StreamableHttpTransport ( url = "http://localhost:8001/mcp" ) 
 client = Client ( transport ) 
 tools = await client . list_tools () 

 CrewAI

 from crewai_tools import BaseTool 
 from fastmcp import Client 

 class NotebookLMTool ( BaseTool ): 
 name = "notebooklm" 
 description = "Chat with NotebookLM" 

 async def _arun ( self , message : str ): 
 client = Client ( "http://localhost:8001/mcp" ) 
 result = await client . call_tool ( "chat_with_notebook" , { "message" : message }) 
 return result 

 🔒 Authentication

 Automatic Setup

 # First time - opens browser for login 
notebooklm-mcp init https://notebooklm.google.com/notebook/abc123

 # Subsequent runs - uses saved session 
notebooklm-mcp --config notebooklm-config.json server

 Manual Setup

 # Interactive browser login 
notebooklm-mcp --config notebooklm-config.json server

 # Check connection 
notebooklm-mcp --config notebooklm-config.json test --notebook YOUR_NOTEBOOK_ID

 🐳 Docker Deployment

 Quick Start

 docker run -e NOTEBOOKLM_NOTEBOOK_ID = "YOUR_ID" notebooklm-mcp

 With Compose

 version : '3.8' 
 services : 
 notebooklm-mcp : 
 image : notebooklm-mcp:latest 
 ports : 
 - "8001:8001" 
 environment : 
 - NOTEBOOKLM_NOTEBOOK_ID=your-notebook-id 
 - TRANSPORT=http 
 volumes : 
 - ./chrome_profile:/app/chrome_profile 

 ⚙️ Configuration

 Config File ( notebooklm-config.json )

 { 
 "default_notebook_id" : "your-notebook-id" , 
 "headless" : true , 
 "timeout" : 30 , 
 "auth" : { 
 "profile_dir" : "./chrome_profile_notebooklm" 
 }, 
 "debug" : false 
 } 

 Environment Variables

 export NOTEBOOKLM_NOTEBOOK_ID = "your-notebook-id" 
 export NOTEBOOKLM_HEADLESS = true 
 export NOTEBOOKLM_DEBUG = false 

 🚀 Performance

 FastMCP v2 Benefits

 ⚡ 5x faster tool registration with decorators

 📋 Auto-generated schemas from Python type hints

 🔒 Built-in validation with Pydantic

 🧪 Better testing and debugging capabilities

 📊 Type safety throughout the stack

 Benchmarks

 Feature 
 Traditional MCP 
 FastMCP v2 

 Tool registration 
 Manual schema 
 Auto-generated 

 Type validation 
 Manual 
 Automatic 

 Error handling 
 Basic 
 Enhanced 

 Development speed 
 Standard 
 5x faster 

 HTTP support 
 Limited 
 Full 

 🛠️ Development

 Setup

 git clone https://github.com/khengyun/notebooklm-mcp
 cd notebooklm-mcp

 # With UV (recommended) 
uv sync --all-groups

 # Or with pip 
pip install -e ".[dev]" 

 Testing

 # Run tests with UV 
uv run pytest

 # With coverage 
uv run pytest --cov = notebooklm_mcp

 # Integration tests 
uv run pytest tests/test_integration.py

 # Or use Taskfile for development 
task test 
task test-coverage

 Code Quality

 # Format code with UV 
uv run black src/ tests/
uv run ruff check src/ tests/

 # Type checking 
uv run mypy src/

 # Or use Taskfile shortcuts 
task format
task lint

 📚 Documentation

 Quick Setup Guide - Get started in 2 minutes

 HTTP Server Guide - Web testing &amp; integration

 FastMCP v2 Guide - Modern MCP features

 Docker Deployment - Production setup

 API Reference - Complete tool documentation

 🔗 Related Projects

 FastMCP - Modern MCP framework

 MCP Specification - Official MCP spec

 NotebookLM - Google's AI notebook

 📄 License

 MIT License - see LICENSE file for details.

 🆘 Support

 Issues : GitHub Issues 

 Discussions : GitHub Discussions 

 Documentation : Read the Docs 

 Built with ❤️ using FastMCP v2 - Modern MCP development made simple! 

 Project links

 Changelog 

 Documentation 

 Homepage 

 Issues 

 Repository 

 Key dates

 PyPI data 
 Data sourced directly from PyPI's database.

 Released: 
 Sep 15, 2025

 Latest release 

1 maintainer 

 PyPI data 
 Data sourced directly from PyPI's database.

 khengyun 

 Credits

Author/Maintainer: 
 NotebookLM MCP Team 

License expression 

 MIT

 View SPDX License List 

 Requires

 Python &gt;=3.10

 Tags

 fastmcp 
 mcp 
 notebooklm 
 automation 
 ai 
 llm 
 fastmcp-v2 

 Classifiers

 Development Status

 5 - Production/Stable

 Intended Audience

 Developers

 Operating System

 OS Independent

 Programming Language

 Python :: 3

 Python :: 3.10

 Python :: 3.11

 Python :: 3.12

 Topic

 Internet :: WWW/HTTP :: Browsers

 Scientific/Engineering :: Artificial Intelligence

 Software Development :: Libraries :: Python Modules

 Report project as malware 

 Download files

Download the file for your platform. If you're not sure which to choose, learn more about installing packages . 

Source Distribution

 notebooklm_mcp-2.0.11.tar.gz 
 (49.5 kB
 view details )

Uploaded 
 Sep 15, 2025
 Source 

Built Distribution

Filter files by name, interpreter, ABI, and platform.

If you're not sure about the file name format, learn more about wheel file names .

The dropdown lists show the available interpreters, ABIs, and platforms. 

Enable javascript to be able to filter the list of wheel files. 

Copy a direct link to the current filters 

Copy 

 File name 

 Interpreter 

 Interpreter 
 py3 

 ABI 

 ABI 
 none 

 Platform 

 Platform 
 any 

 notebooklm_mcp-2.0.11-py3-none-any.whl 
 (26.8 kB
 view details )

Uploaded 
 Sep 15, 2025
 Python 3 

 File details

 Details for the file notebooklm_mcp-2.0.11.tar.gz .

 File metadata

 Download URL: notebooklm_mcp-2.0.11.tar.gz 

 Upload date: 
 Sep 15, 2025

Size: 49.5 kB 

 Tags: Source

Uploaded using Trusted Publishing? No 

 Uploaded via: twine/6.1.0 CPython/3.13.7

 File hashes

 Hashes for notebooklm_mcp-2.0.11.tar.gz 

 Algorithm 
 Hash digest 

 SHA256 

 3aa15e68a5f5da59500257c45c5f2d7fa1e6d87a463581f7e733984153a8ac9f 

Copy 

 MD5 

 b5d6be15dd52aabec429401638274ac1 

Copy 

 BLAKE2b-256 

 fa3a8e2d9131a09ac6833dd5dab6ab1401596e23275a1bcf3e9f54fa17c1487d 

Copy 

 See more details on using hashes here. 

 File details

 Details for the file notebooklm_mcp-2.0.11-py3-none-any.whl .

 File metadata

 Download URL: notebooklm_mcp-2.0.11-py3-none-any.whl 

 Upload date: 
 Sep 15, 2025

Size: 26.8 kB 

 Tags: Python 3

Uploaded using Trusted Publishing? No 

 Uploaded via: twine/6.1.0 CPython/3.13.7

 File hashes

 Hashes for notebooklm_mcp-2.0.11-py3-none-any.whl 

 Algorithm 
 Hash digest 

 SHA256 

 83d596538f13d136d4c7dc1d5e7b9dc473f2544a3cb61a0420ff0dd04112343f 

Copy 

 MD5 

 256f15d163ef6fd232fdcf5718d12f7b 

Copy 

 BLAKE2b-256 

 c7e8edeb1395aa312cc3122399695ff35a0cd51277bbde7b4974c140876525ab 

Copy 

 See more details on using hashes here. 

 Release history 

 Release notifications |
 RSS feed 

 This release 

 2.0.11

 Sep 15, 2025

 2.0.10

 Sep 15, 2025

 2.0.9

 Sep 15, 2025

 2.0.8

 Sep 15, 2025

 2.0.7

 Sep 15, 2025

 2.0.6

 Sep 15, 2025

 Help

 Installing packages 

 Uploading packages 

 User guide 

 Project name retention 

 FAQs 

 About PyPI

 PyPI Blog 

 Infrastructure dashboard 

 Statistics 

 Logos & trademarks 

 Our sponsors 

 Contributing to PyPI

 Bugs and feedback 

 Contribute on GitHub 

 Translate PyPI 

 Sponsor PyPI 

 Development credits 

 Using PyPI

 Terms of Service 

 Report security issue 

 Code of conduct 

 Privacy Notice 

 Acceptable Use Policy 

Status: 
 all systems operational 

Developed and maintained by the Python community, for the Python community. 

 Donate today! 

 "PyPI", "Python Package Index", and the blocks logos are registered trademarks of the Python Software Foundation .

 © 2026 Python Software Foundation 

 Site map 

Deployed from bd8ccde 

 Switch to desktop version 

 English 

 español 

 français 

 日本語 

 português (Brasil) 

 українська 

 Ελληνικά 

 Deutsch 

 中文 (简体) 

 中文 (繁體) 

 русский 

 עברית 

 Esperanto 

 한국어 

 Supported by

 AWS 

 Cloud computing and Security Sponsor

 Datadog 

 Monitoring

 Depot 

 Continuous Integration

 Fastly 

 CDN

 Google 

 Download Analytics

 Pingdom 

 Monitoring

 Sentry 

 Error logging

 StatusPage 

 Status page