---
layout: single
title: "Coffee Roulette Architecture"
date: 2024-06-22
categories: architecture
tags: [slack, bot, architecture]
---

# Coffee Roulette Slack Bot Architecture

This page walks through the architecture of how the Coffee Roulette bot was built.

## Overview

The Coffee Roulette bot is designed to pair users for coffee chats based on their reactions to a weekly Slack post.
It is designed in a way that allows it to be redeployed across channels, and is now actively used within the WTC and AES clusters.

## Components

- **Slack App**: Manages the interaction with Slack, including posting messages and handling reactions.
- **AI Functions**: Generates the weekly message content using generative AI powered by Watsonx APIs
- **File Operations**: Handles logging and reading reactions, storing timestamps, and other file-based operations necessary for the bot's functionality.

![Architecture Diagram](assets/images/architecture-diagram.png)

## Detailed Walkthrough

### Slack App

The Slack app uses the Bolt framework to interact with the Slack API. It posts messages, adds reactions, and handles events.

### AI Functions

These functions use Watsonx generative AI APIs to generate the weekly message content. They ensure the content is engaging and appropriate for the Coffee Roulette context.

### File Operations

Handles logging and reading user reactions, storing timestamps, and other file-based operations necessary for the bot's functionality.

## Conclusion

The Coffee Roulette bot is an example of integrating AI-generated content with user interaction on Slack to foster community engagement. For any issues or bugs, please contact @Josh Robertson.

