# AI-Powered Job Recommendation System

This project is an AI-powered job recommendation system that fetches jobs using web scraping, processes descriptions with NLP, and generates recommendations using content-based and collaborative filtering.

## Project Structure

- `/scraper`: Scrapy spider files for fetching job postings.
- `/nlp`: NLP pipeline using spaCy and SBERT for text processing and embedding.
- `/recommender`: Recommendation engine (content-based and collaborative filtering).
- `/alerts`: Email notification module.
- `/web`: Flask web application.
- `/database`: Database schema and access layer.
- `/tests`: PyTest unit tests.
