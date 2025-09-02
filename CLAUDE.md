# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal repository called "PublicPortal" that appears to be in the initial setup phase. Based on the directory name and MCP configuration, this project is intended to work with public data portals.

## MCP Configuration

The project is configured to use the OpenData MCP server (`mcp__iosif-2-opendata-mcp__search_api`) which provides access to Korean public data portal APIs. This suggests the project will likely:

- Search and access public datasets
- Integrate with Korean government open data APIs
- Potentially build a portal or interface for public data consumption

## Current State

The repository currently contains:
- `.claude/settings.local.json` - Claude Code configuration with OpenData MCP permissions
- `start.md` - Empty placeholder file

## Development Setup

Since no build system, dependencies, or source code structure has been established yet, the initial development will need to:

1. Determine the target programming language and framework
2. Set up appropriate project configuration files (package.json, requirements.txt, etc.)
3. Establish project structure and architecture
4. Configure build, test, and deployment workflows

## MCP Server Usage

When working with the OpenData MCP server, use:
- `mcp__iosif-2-opendata-mcp__search_api` for searching public datasets
- `mcp__iosif-2-opendata-mcp__get_std_docs` for retrieving dataset documentation  
- `mcp__iosif-2-opendata-mcp__fetch_data` for accessing actual data from APIs