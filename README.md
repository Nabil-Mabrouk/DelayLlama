# App Name: D-Llama

on streamlit cloud : [Delay-Llama](https://delayllama.streamlit.app/)

## Purpose

D-Llama is an application designed to assist users in analyzing and making informed decisions in the cryptocurrency market. It leverages various data sources and a conversational interface to provide market insights, technical analysis, and news updates.

## Key Features

### Market Data Retrieval

- The app fetches up-to-date cryptocurrency market data, including open, close, high, low, and volume for Bitcoin (BTC) at 1-hour intervals.
- It calculates technical indicators such as moving averages (SMA and EMA), Relative Strength Index (RSI), price variations, and volatility.

### Cryptocurrency News

- The app scrapes cryptocurrency news from the web, focusing on Bitcoin (BTC).
- News articles are processed and organized for user access.

### Conversational Interface

- Users can interact with the app by typing questions or requests related to the cryptocurrency market.
- The app processes user queries and responds with relevant information.

### Large Language Models and Clarifai Integration

- The app integrates Large Language Models with Clarifai, a service that can process text data.
- It uses llm to assist in answering user questions and providing specific data from the market dataset.

### User-Friendly UI

- The Streamlit-based user interface is user-friendly, allowing users to easily enter questions and receive responses.
- Users can select different models to answer their questions, including technical analysis models and more.

## How It Works

Users input questions or requests related to the cryptocurrency market into the app's interface. The app processes user queries step by step, extracting necessary data from the cryptocurrency market dataset. For complex questions, the app uses the llm integration to assist in generating relevant Python code to retrieve specific data. Users receive responses that may include technical analysis, market insights, or relevant news articles.

**Note:** While the app provides valuable information and analysis, it's essential to use it as a tool for gaining insights into the cryptocurrency market. Always exercise caution and do thorough research before making financial decisions in the volatile cryptocurrency market.

## Enhancements and Future Development

This app can be extended to include support for more cryptocurrencies and additional technical indicators. User authentication and personalization features can be added to save user preferences and historical queries. Integration with real-time market data APIs can provide even more up-to-the-minute information. Continuous monitoring and automation of data updates can be implemented to keep the information current. Overall, D-Llama serves as a handy tool for cryptocurrency enthusiasts and traders seeking market insights and analysis in a conversational and user-friendly manner.
