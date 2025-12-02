# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SourceInfo is a database project for collecting and organizing information about news sources and content publishers. The goal is to support content rating and analysis across various projects by providing metadata about source quality, credibility, and characteristics.

## Data Collection Approach

This project uses **Playwright MCP with human-in-the-loop** to gather information from web sources, including:
- Subscription-based sites requiring authentication
- Paywalled content sources
- Public news outlets and publishers

When collecting data, coordinate with the user for authentication steps and navigation through protected content.

## Project Status

This is an early-stage project focused on building a foundational database. The initial phase involves:
1. Gathering basic data on frequently visited and popular news sources
2. Establishing data structures and schemas for source metadata
3. Creating tools and workflows for efficient data collection

## Architecture Considerations

As the project develops, key architectural decisions will include:
- Data storage format (JSON files, SQLite, or other database)
- Metadata schema for sources (bias ratings, credibility scores, ownership, topic focus, etc.)
- Integration patterns for using this data in downstream projects
- Update and maintenance strategies for keeping source information current
