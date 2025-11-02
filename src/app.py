import base64
import re
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from textwrap import dedent

import joblib
import pandas as pd
import streamlit as st


APP_STYLE = r"""/* Global layout */
body {
    font-family: "Inter", "Segoe UI", sans-serif;
    background: #f5f7fb;
    color: #0f172a;
}

.main > div {
    padding: 24px 56px 56px;
}

.centered-text {
    text-align: center;
    margin-top: 32px;
    color: #1e293b;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    padding: 12px 24px;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #1b6ac9;
}

.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    gap: 12px;
}

/* Buttons */
button[kind="primary"],
div.stButton > button {
    border-radius: 999px;
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    color: #fff;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    border: none;
    box-shadow: 0 8px 16px rgba(27, 106, 201, 0.25);
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 18px rgba(27, 106, 201, 0.3);
}

button[data-testid="baseButton-secondary"] {
    border-radius: 999px;
    border: 1px solid #cfd8e3;
    background: #fff;
    color: #1b2a4b;
    font-weight: 600;
    padding: 0.5rem 1.4rem;
}

/* Card components */
.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
}

.card h3,
.card h4 {
    margin: 0 0 8px;
    font-size: 20px;
    color: #0f172a;
}

.card p {
    margin-bottom: 6px;
    line-height: 1.55;
    color: #475569;
}

.pill {
    display: inline-flex;
    align-items: center;
    background: rgba(27, 106, 201, 0.12);
    color: #1b6ac9;
    border-radius: 999px;
    padding: 4px 12px;
    margin: 4px 6px 4px 0;
    font-size: 13px;
    font-weight: 600;
}

.tag-list {
    display: flex;
    flex-wrap: wrap;
}

.card-footer {
    margin-top: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.card-footer span {
    font-weight: 600;
    color: #475569;
}

.empty-state {
    text-align: center;
    color: #475569;
    padding: 32px;
}

/* Job match page */
.job-match-hero {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
}

.job-hero-copy h2 {
    margin: 0;
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
}

.job-hero-copy p {
    margin: 8px 0 28px;
    color: #64748b;
    max-width: 540px;
}

.job-filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: flex-end;
}

.job-filter-bar .filter-field {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1 1 200px;
}

.job-filter-bar .filter-field.wide {
    flex-basis: 320px;
}

.job-filter-bar label {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
}

.input-shell {
    position: relative;
    display: flex;
    align-items: center;
    border-radius: 12px;
    border: 1px solid #d0d9e5;
    background: #f8fafc;
    padding: 12px 16px;
    gap: 8px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-shell:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.08);
    background: #ffffff;
}

.input-shell input,
.input-shell select {
    border: none;
    outline: none;
    width: 100%;
    font-size: 14px;
    background: transparent;
    color: #0f172a;
}

.input-shell select {
    appearance: none;
    padding-right: 20px;
}

.input-icon {
    font-size: 16px;
    color: #94a3b8;
    line-height: 1;
}

.filter-button {
    align-self: stretch;
    padding: 14px 32px;
    border-radius: 12px;
    border: none;
    background: #2563eb;
    color: #ffffff;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.filter-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.22);
}

.job-results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.job-results-header h3 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
}

.job-results-header p {
    margin: 4px 0 0;
    color: #64748b;
}

/* Learning path */
.learning-hero {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 32px;
    background: #ffffff;
    border-radius: 24px;
    border: 1px solid #e2e8f0;
    padding: 40px;
    margin-bottom: 32px;
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.05);
}

.hero-copy {
    flex: 1 1 360px;
}

.hero-eyebrow {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2563eb;
    margin-bottom: 8px;
}

.hero-copy h2 {
    margin: 0 0 12px;
    font-size: 32px;
    font-weight: 700;
    color: #0f172a;
}

.hero-description {
    max-width: 520px;
    color: #475569;
    margin-bottom: 18px;
}

.hero-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.hero-chip {
    background: rgba(37, 99, 235, 0.12);
    color: #1d4ed8;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
}

.hero-chip.muted {
    background: #e2e8f0;
    color: #64748b;
}

.hero-metrics {
    display: grid;
    grid-template-columns: repeat(3, minmax(140px, 1fr));
    gap: 16px;
    flex: 1 1 320px;
}

.hero-metric {
    background: #f8fafc;
    border-radius: 18px;
    padding: 24px 20px;
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
}

.metric-caption {
    font-size: 13px;
    color: #64748b;
}

.learning-path-list {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.learning-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 32px;
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.06);
}

.learning-card-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 24px;
    align-items: flex-start;
    margin-bottom: 18px;
}

.learning-card-title h3 {
    margin: 4px 0 6px;
    font-size: 24px;
    font-weight: 700;
}

.card-eyebrow {
    font-size: 13px;
    font-weight: 600;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.card-meta {
    color: #64748b;
    margin: 0;
}

.learning-card-progress {
    min-width: 200px;
    max-width: 260px;
}

.progress-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
}

.progress-track {
    position: relative;
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: #e2e8f0;
    margin: 10px 0;
    overflow: hidden;
}

.progress-fill {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #f97316, #f59e0b);
    border-radius: inherit;
}

.progress-value {
    font-weight: 700;
    color: #f97316;
}

.learning-card-description {
    color: #475569;
    margin: 0 0 24px;
}

.learning-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.grid-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.grid-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    color: #475569;
}

.grid-value {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
}

.learning-card-skills {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 28px;
}

.pill.muted {
    background: #e2e8f0;
    color: #64748b;
}

.learning-card-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.ghost-button,
.primary-button {
    border-radius: 999px;
    font-weight: 600;
    padding: 12px 28px;
    border: none;
    cursor: pointer;
    font-size: 15px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.ghost-button {
    background: #ffffff;
    color: #1d4ed8;
    border: 1px solid #cbd5f5;
}

.primary-button {
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    color: #ffffff;
    box-shadow: 0 12px 24px rgba(27, 106, 201, 0.28);
}

.ghost-button:hover,
.primary-button:hover {
    transform: translateY(-1px);
}

.primary-button:hover {
    box-shadow: 0 14px 26px rgba(27, 106, 201, 0.35);
}

.ghost-button.small {
    padding: 8px 18px;
    font-size: 14px;
}

@media (max-width: 980px) {
    .hero-metrics {
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    }
}

.results-count {
    background: #eef2ff;
    color: #1d4ed8;
    border-radius: 999px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 14px;
}

/* Home dashboard */
.home-dashboard {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.home-header {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    align-items: center;
    gap: 18px;
    background: #ffffff;
    padding: 24px 32px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
}

.home-header-copy h2 {
    margin: 0;
    font-size: 28px;
}

.home-header-copy p {
    margin: 4px 0 0;
    color: #64748b;
}

.home-header-search {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #f1f5f9;
    padding: 12px 16px;
    border-radius: 999px;
    border: 1px solid #dbe4f3;
}

.home-header-search input {
    border: none;
    background: transparent;
    width: 100%;
    font-size: 15px;
    outline: none;
    color: #0f172a;
}

.home-header-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: flex-end;
}

.chip-label {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.chip-value {
    background: #1b6ac9;
    color: #ffffff;
    border-radius: 999px;
    padding: 6px 16px;
    font-weight: 600;
}

.home-grid {
    display: grid;
    gap: 24px;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
}

.card-subtitle {
    margin: 4px 0 0;
    color: #64748b;
    max-width: 440px;
}

.timeline-legend {
    display: flex;
    gap: 8px;
}

.legend-pill {
    background: rgba(27, 106, 201, 0.14);
    color: #1b4fd8;
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 13px;
}

.legend-pill.upcoming {
    background: rgba(148, 163, 184, 0.2);
    color: #475569;
}

.timeline-month-header {
    display: grid;
    grid-template-columns: repeat(16, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 18px;
}

.timeline-month {
    background: #f8fafc;
    border: 1px dashed #cbd5f5;
    border-radius: 14px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.month-name {
    font-weight: 600;
    color: #0f172a;
}

.month-weeks {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 6px;
    font-size: 12px;
    color: #64748b;
}

.timeline-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.timeline-row {
    display: grid;
    grid-template-columns: minmax(0, 260px) minmax(0, 1fr);
    align-items: center;
    gap: 24px;
}

.timeline-label {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.timeline-eyebrow {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.timeline-title {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
}

.timeline-provider {
    font-size: 14px;
    color: #64748b;
}

.timeline-track {
    position: relative;
    display: grid;
    grid-template-columns: repeat(16, minmax(0, 1fr));
    gap: 8px;
    height: 48px;
    align-items: center;
    border-radius: 16px;
    padding: 4px 0;
    overflow: hidden;
}

.timeline-track::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: rgba(15, 23, 42, 0.02);
    background-image: repeating-linear-gradient(
        to right,
        rgba(148, 163, 184, 0.35),
        rgba(148, 163, 184, 0.35) 1px,
        transparent 1px,
        transparent calc(100% / 16)
    );
    pointer-events: none;
}

.timeline-bar {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 44px;
    background: linear-gradient(135deg, rgba(27, 106, 201, 0.85), rgba(63, 166, 255, 0.75));
    color: #ffffff;
    border-radius: 14px;
    box-shadow: 0 10px 22px rgba(27, 106, 201, 0.25);
    font-weight: 600;
    font-size: 14px;
    padding: 0 12px;
    text-align: center;
    z-index: 1;
}

.timeline-bar span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.progress-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.progress-row {
    display: grid;
    grid-template-columns: minmax(0, 240px) minmax(0, 1fr) 60px 120px;
    align-items: center;
    gap: 16px;
}

.progress-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.progress-name {
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
}

.progress-provider {
    font-size: 13px;
    color: #64748b;
}

.progress-meter {
    position: relative;
    background: #e2e8f0;
    border-radius: 999px;
    height: 12px;
    overflow: hidden;
}

.progress-fill {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    border-radius: 999px;
}

.progress-value {
    font-weight: 700;
    color: #0f172a;
}

.progress-visibility {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
}

.search-icon {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid #64748b;
    position: relative;
}

.search-icon::after {
    content: "";
    position: absolute;
    width: 8px;
    height: 2px;
    background: #64748b;
    top: 12px;
    left: 12px;
    transform: rotate(45deg);
    border-radius: 2px;
}

@media (max-width: 1024px) {
    .timeline-row {
        grid-template-columns: 1fr;
    }

    .progress-row {
        grid-template-columns: 1fr;
        gap: 12px;
    }

    .progress-value,
    .progress-visibility {
        justify-self: flex-start;
    }
}


.job-detail-wrapper {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: 24px;
    align-items: start;
}

.job-detail-main,
.job-detail-sidebar {
    min-width: 0;
}

.detail-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
    display: flex;
    flex-direction: column;
    gap: 28px;
}

.detail-header h2 {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
}

.detail-header p {
    margin: 8px 0 0;
    color: #475569;
    font-size: 15px;
}

.detail-section h3 {
    margin: 0 0 12px;
    font-size: 18px;
    color: #0f172a;
}

.detail-section p {
    margin: 0;
    color: #475569;
    line-height: 1.6;
}

.detail-list {
    margin: 0;
    padding-left: 20px;
    color: #475569;
    line-height: 1.6;
}

.detail-list li {
    margin-bottom: 8px;
}

.job-detail-sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.job-summary-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.summary-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.summary-label {
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
}

.summary-value {
    font-size: 15px;
    color: #0f172a;
    font-weight: 600;
}

.summary-group.highlight {
    padding: 12px 16px;
    border-radius: 18px;
    background: #f1f8ff;
}

.summary-group.highlight .summary-value.score {
    font-size: 24px;
    color: #1b6ac9;
}

.apply-button {
    margin-top: 8px;
    width: 100%;
    padding: 14px 20px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    color: #ffffff;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 10px 24px rgba(27, 106, 201, 0.25);
}

.apply-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 28px rgba(27, 106, 201, 0.3);
}

.sidebar-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.sidebar-card h4 {
    margin: 0 0 8px;
    font-size: 18px;
    color: #0f172a;
}

.sidebar-text {
    margin: 0 0 16px;
    color: #475569;
    line-height: 1.6;
}

.contact-chip {
    display: inline-flex;
    align-items: center;
    padding: 8px 14px;
    border-radius: 999px;
    background: #eef4ff;
    color: #1b6ac9;
    font-weight: 600;
    font-size: 14px;
}

.job-detail-empty {
    text-align: center;
    color: #475569;
}

@media (max-width: 1100px) {
    .job-detail-wrapper {
        grid-template-columns: 1fr;
    }
}

/* Profile page */
.profile-page {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.profile-header {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 28px;
    align-items: center;
}

.profile-avatar img {
    width: 120px;
    height: 120px;
    object-fit: cover;
    border-radius: 24px;
    border: 4px solid #e2e8f0;
}

.avatar-fallback {
    width: 120px;
    height: 120px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    color: #fff;
    font-weight: 700;
    font-size: 32px;
}

.profile-summary h2 {
    font-size: 28px;
    margin-bottom: 4px;
}

.profile-role {
    margin: 0 0 18px;
    color: #64748b;
    font-weight: 500;
}

.profile-meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px 24px;
}

.meta-label {
    display: block;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 4px;
}

.meta-value {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
}

.profile-actions button {
    cursor: pointer;
}

.profile-actions .button {
    border-radius: 999px;
    padding: 12px 20px;
    font-weight: 600;
    border: 1px solid #cbd5f5;
    background: #eef2ff;
    color: #3730a3;
}

.profile-actions .button.ghost {
    background: #f8fafc;
    border-color: #e2e8f0;
    color: #1e293b;
}

.profile-highlights {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}

.mini-card {
    background: #f8fafc;
    border-radius: 16px;
    padding: 18px 20px;
    border: 1px solid #e2e8f0;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.mini-label {
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
}

.mini-value {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: #0f172a;
    margin: 6px 0;
}

.mini-caption {
    font-size: 13px;
    color: #64748b;
}

.section-card {
    padding: 32px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
}

.section-header h3 {
    margin: 0;
    font-size: 22px;
}

.section-description {
    margin: 6px 0 0;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}

.detail-grid.single-column {
    grid-template-columns: 1fr;
}

.detail-label {
    display: block;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 6px;
}

.detail-value {
    font-size: 15px;
    color: #1f2937;
    font-weight: 600;
}

.skill-matrix {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.skill-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.skill-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.skill-name {
    font-weight: 600;
    color: #0f172a;
}

.skill-level {
    font-size: 13px;
    color: #475569;
}

.progress-track {
    background: #e2e8f0;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(135deg, #1b6ac9, #3fa6ff);
    border-radius: inherit;
}

.empty-copy {
    font-size: 14px;
    color: #94a3b8;
}
.job-card {
    position: relative;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    display: flex;
    gap: 24px;
    align-items: flex-start;
}

.job-card:hover {
    border-color: #c7d2fe;
    box-shadow: 0 16px 32px rgba(37, 99, 235, 0.12);
    transform: translateY(-2px);
}

.job-card.is-active {
    border-color: #2563eb;
    box-shadow: 0 18px 40px rgba(37, 99, 235, 0.18);
}

.job-card-leading {
    flex: 0 0 56px;
    display: flex;
    justify-content: center;
}

.job-card-badge {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: linear-gradient(135deg, #e0e7ff, #eff6ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #1d4ed8;
    font-size: 18px;
}

.job-card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.job-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
}

.job-card-title {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.job-card-link {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    text-decoration: none;
    transition: color 0.2s ease;
}

.job-card-link::after {
    content: "\2192";
    font-size: 18px;
    opacity: 0;
    transform: translateX(-6px);
    transition: transform 0.2s ease, opacity 0.2s ease;
}

.job-card-link:hover {
    color: #2563eb;
}

.job-card-link:hover::after {
    opacity: 1;
    transform: translateX(0);
}

.job-card.is-active .job-card-link {
    color: #2563eb;
}

.match-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eef2ff;
    color: #1d4ed8;
    border-radius: 999px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 14px;
    white-space: nowrap;
}

.job-card-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #64748b;
    font-size: 14px;
}

.job-card-meta .dot {
    width: 4px;
    height: 4px;
    border-radius: 999px;
    background: currentColor;
    display: inline-block;
}

.job-card-highlights {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.job-card-highlights .pill {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid transparent;
}


.job-card-highlights .pill.soft {
    background: #e0ecff;
    color: #1d4ed8;
}

.job-card-highlights .pill.muted {
    background: #f1f5f9;
    color: #475569;
}

.job-card-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.job-card-skills .pill {
    border-radius: 10px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #1e293b;
}

.job-card-skills .pill.muted {
    background: #f1f5f9;
    color: #475569;
}
"""


def apply_custom_style() -> None:
    """Inject CSS from the bundled stylesheet."""
    st.markdown(f"<style>{APP_STYLE}</style>", unsafe_allow_html=True)


REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"



_FALLBACK_HOME_MODULES: List[Dict[str, Any]] = [
    {
        "title": "Advanced Analytics Platform",
        "provider": "SkillGraph Academy",
        "duration": 24.0,
        "score": 86.0,
        "visibility": 100.0,
        "progress": 68.0,
    },
    {
        "title": "Assessed Talent Patterns",
        "provider": "SkillGraph Academy",
        "duration": 18.0,
        "score": 74.0,
        "visibility": 92.0,
        "progress": 54.0,
    },
    {
        "title": "TopTalent Insights",
        "provider": "SkillGraph Academy",
        "duration": 20.0,
        "score": 68.0,
        "visibility": 88.0,
        "progress": 49.0,
    },
    {
        "title": "System Integrations Fundamentals",
        "provider": "SkillGraph Academy",
        "duration": 22.0,
        "score": 64.0,
        "visibility": 84.0,
        "progress": 42.0,
    },
    {
        "title": "Capacity Planning Essentials",
        "provider": "SkillGraph Academy",
        "duration": 16.0,
        "score": 59.0,
        "visibility": 80.0,
        "progress": 37.0,
    },
]

def _render_tags(items: Iterable[str]) -> str:
    tags = [f"<span class='pill'>{escape(item.strip())}</span>" for item in items if item and item.strip()]
    return "".join(tags)


def _safe_split(value: str) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [piece.strip() for piece in str(value).split(",") if piece.strip()]


def _image_as_data_uri(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{path.suffix.lstrip('.')};base64,{encoded}"


def _get_profile_image(user_id: str) -> Optional[str]:
    if not user_id:
        return None
    candidate = IMAGES_DIR / f"{user_id}.jpg"
    return _image_as_data_uri(candidate)


def _initials(user: dict) -> str:
    first = str(user.get("first_name", "")).strip()[:1]
    last = str(user.get("last_name", "")).strip()[:1]
    initials = (first + last).upper()
    return initials or "SG"


def _pair_skills(user: dict) -> List[Tuple[str, str]]:
    names = _safe_split(user.get("skill_name", []))
    levels = _safe_split(user.get("skill_level", []))
    if len(levels) < len(names):
        levels.extend([""] * (len(names) - len(levels)))
    elif len(levels) > len(names):
        names.extend(["Skill"] * (len(levels) - len(names)))
    return list(zip(names, levels))


_LEVEL_DETAILS = {
    "L1": {"label": "Beginner", "score": 25},
    "L2": {"label": "Intermediate", "score": 50},
    "L3": {"label": "Advanced", "score": 75},
    "L4": {"label": "Expert", "score": 100},
}


def _render_skill_rows(user: dict) -> str:
    """Render each skill row as single-line HTML (no newline, no indent)."""
    rows = []
    for name, raw_level in _pair_skills(user):
        details = _LEVEL_DETAILS.get(raw_level.strip().upper(), {"label": "Unknown", "score": 10})
        row = (
            "<div class='skill-row'>"
            "<div class='skill-info'>"
            f"<span class='skill-name'>{name}</span>"
            f"<span class='skill-level'>{details['label']}</span>"
            "</div>"
            "<div class='progress-track'>"
            f"<div class='progress-bar' style='width:{details['score']}%'></div>"
            "</div>"
            "</div>"
        )
        rows.append(row)
    return "".join(rows)


def show_profile_card(user: dict) -> None:
    """Display the profile view in Streamlit with real HTML rendering."""
    user_id = user.get("user_id", "")
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip() or "Unnamed employee"
    image_data_uri = _get_profile_image(user_id)
    initials = _initials(user)
    gpa = user.get("gpa", "-")
    degree = user.get("degree_type", "-")
    major = user.get("major", "-")
    city = user.get("city", "-")

    # Render skill section
    skills_markup = _render_skill_rows(user)
    if not skills_markup:
        skills_markup = "<div class='empty-copy'>No skills registered yet.</div>"

    skill_pairs = _pair_skills(user)
    total_skills = len(skill_pairs)
    tracked_levels = [
        _LEVEL_DETAILS.get(level.strip().upper(), {"score": 0})["score"]
        for _, level in skill_pairs
    ]
    avg_level = int(round(sum(tracked_levels) / total_skills)) if total_skills else 0

    # HTML content (no indent)
    html = f"""
<div class="profile-page">

<section class="card profile-header">
    <div class="profile-avatar">
        {f'<img src="{image_data_uri}" alt="Profile photo" />' if image_data_uri else f"<div class='avatar-fallback'>{initials}</div>"}
    </div>
    <div class="profile-summary">
        <h2>{full_name}</h2>
        <p class="profile-role">{major or 'Specialisation unavailable'}</p>
        <div class="profile-meta">
            <div class="meta-item"><span class="meta-label">Employee ID</span><span class="meta-value">{user_id or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">Degree</span><span class="meta-value">{degree or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">GPA</span><span class="meta-value">{gpa or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">Location</span><span class="meta-value">{city or '—'}</span></div>
        </div>
    </div>
    <div class="profile-actions">
        <button class="button ghost">View performance</button>
    </div>
</section>

<section class="profile-highlights">
    <div class="mini-card">
        <span class="mini-label">Skills tracked</span>
        <span class="mini-value">{total_skills}</span>
        <span class="mini-caption">Declared competencies</span>
    </div>
    <div class="mini-card">
        <span class="mini-label">Average proficiency</span>
        <span class="mini-value">{avg_level}%</span>
        <span class="mini-caption">Across registered skills</span>
    </div>
    <div class="mini-card">
        <span class="mini-label">Academic score</span>
        <span class="mini-value">{gpa or '—'}</span>
        <span class="mini-caption">Latest reported GPA</span>
    </div>
</section>

<section class="card section-card">
    <div class="section-header">
        <div>
            <h3>Employee overview</h3>
            <p class="section-description">Key background information pulled from the employee registry.</p>
        </div>
    </div>
    <div class="detail-grid">
        <div><span class="detail-label">First name</span><span class="detail-value">{first_name or '—'}</span></div>
        <div><span class="detail-label">Last name</span><span class="detail-value">{last_name or '—'}</span></div>
        <div><span class="detail-label">Specialisation</span><span class="detail-value">{major or '—'}</span></div>
        <div><span class="detail-label">Highest degree</span><span class="detail-value">{degree or '—'}</span></div>
        <div><span class="detail-label">Current city</span><span class="detail-value">{city or '—'}</span></div>
        <div><span class="detail-label">GPA</span><span class="detail-value">{gpa or '—'}</span></div>
    </div>
</section>

<section class="card section-card">
    <div class="section-header">
        <div>
            <h3>Skill proficiency</h3>
            <p class="section-description">Latest proficiency ratings for each declared skill.</p>
        </div>
    </div>
    <div class="skill-matrix">{skills_markup}</div>
</section>

<section class="card section-card">
    <div class="section-header">
        <div>
            <h3>Development recommendations</h3>
            <p class="section-description">Explore tailored job matches and courses to continue professional growth.</p>
        </div>
    </div>
    <div class="detail-grid single-column">
        <div>
            <span class="detail-label">Job matches</span>
            <span class="detail-value">Review the <strong>Job Match</strong> tab for roles that align with this profile.</span>
        </div>
        <div>
            <span class="detail-label">Learning path</span>
            <span class="detail-value">Visit the <strong>Learning Path</strong> tab to identify courses that close remaining skill gaps.</span>
        </div>
    </div>
</section>

</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def show_job_cards(jobs_df: pd.DataFrame) -> Optional[str]:
    """Render job recommendations as modern cards with inline detail (no page reload, same UI)."""

    def _job_identifier(row: pd.Series, fallback: int) -> str:
        for key in ("jid", "job_id", "id"):
            if key in row and pd.notna(row[key]):
                value = str(row[key]).strip()
                if value:
                    return value
        return str(fallback)

    active_job_id = st.session_state.get("selected_job_id")
    active_job_id = str(active_job_id) if active_job_id is not None else None

    for index, row in jobs_df.iterrows():
        job_id = _job_identifier(row, index)
        is_active = active_job_id == job_id

        raw_job_title = (
            row.get("job_title")
            or row.get("title")
            or row.get("jid")
            or "Untitled role"
        )
        job_title = escape(str(raw_job_title))
        company = escape(str(row.get("company") or "Unknown company"))
        location = escape(str(row.get("location") or "Location not specified"))
        employment_type = escape(str(row.get("employment_type") or row.get("job_type") or "Full-time"))
        salary = escape(str(row.get("salary_range") or row.get("salary") or "Salary not disclosed"))
        experience = escape(str(row.get("experience_level") or row.get("level") or "All levels"))
        posted = escape(str(row.get("posted") or row.get("timeline") or "Just posted"))

        score = row.get("score")
        score_value = None
        if pd.notna(score):
            try:
                numeric_score = float(score)
                score_value = numeric_score * 100 if numeric_score <= 1 else numeric_score
            except (TypeError, ValueError):
                score_value = None
        match_label = f"Match {score_value:.0f}%" if score_value is not None else "Match —"

        skills = _render_tags(_safe_split(row.get("proj_quals", ""))) or "<span class='pill muted'>Skills unavailable</span>"

        initials_source = row.get("company") or raw_job_title
        initials = (str(initials_source)[:1].upper() if initials_source and str(initials_source).strip() else "J")

        card_classes = "job-card"
        if is_active:
            card_classes += " is-active"

        highlights = dedent(f"""
            <div class='job-card-highlights'>
                <span class='pill soft'>{employment_type}</span>
                <span class='pill soft'>{experience}</span>
                <span class='pill muted'>{salary}</span>
                <span class='pill muted'>{posted}</span>
            </div>
        """).strip()

        job_id_str = str(job_id)

        # render card HTML
        card_html = dedent(f"""
            <article class="{card_classes}">
                <div class="job-card-leading">
                    <div class="job-card-badge" aria-hidden="true">{escape(initials)}</div>
                </div>
                <div class="job-card-content">
                    <div class="job-card-header">
                        <div class="job-card-title">
                            <span class="job-card-link" style="cursor:pointer; color:#0073e6;" title="Click to view details">
                                {job_title}
                            </span>
                        </div>
                        <span class="match-chip">{match_label}</span>
                    </div>
                    <div class="job-card-meta">
                        <span>{company}</span><span class="dot"></span><span>{location}</span>
                    </div>
                    {highlights}
                    <div class="job-card-skills" aria-label="Key skills">{skills}</div>
                </div>
            </article>
        """).strip()

        # Hiển thị card
        st.markdown(card_html, unsafe_allow_html=True)

        # Thêm nút vô hình để kích hoạt hành vi click
        if st.button(job_title, key=f"btn_{job_id}", use_container_width=True):
            st.session_state.selected_job_id = job_id
            st.rerun()

        # Nếu job này đang active → hiển thị detail ngay bên dưới
        if is_active:
            show_job_detail(row)
            if st.button("Hide details", key=f"hide_{job_id}", use_container_width=True):
                st.session_state.selected_job_id = None
                st.rerun()
            st.markdown("---")

    return st.session_state.get("selected_job_id")


def _derive_job_highlights(description: Optional[str]) -> Tuple[str, List[str]]:
    if not description or (isinstance(description, float) and pd.isna(description)):
        return "Job overview is not available for this role yet.", []

    text = str(description)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    segments = [segment.strip("•- \u2022") for segment in text.split("\n") if segment.strip()]

    if not segments:
        cleaned = re.split(r"(?<=[.!?])\s+", text)
        segments = [segment.strip("•- ") for segment in cleaned if segment.strip()]

    if not segments:
        return "Job overview is not available for this role yet.", []

    overview = segments[0]
    responsibilities = segments[1:] or []
    return overview, responsibilities


def show_job_detail(job: Optional[pd.Series]) -> None:
    """Render a detailed job preview panel."""

    if job is None:
        st.markdown(
            "<div class='job-detail-empty card'>Select a job from the list to view its full description.</div>",
            unsafe_allow_html=True,
        )
        return

    if isinstance(job, pd.Series):
        job_data = job.to_dict()
    else:
        job_data = job or {}

    def _clean(value: Optional[str], fallback: str = "—") -> str:
        if value is None:
            return fallback
        if isinstance(value, float) and pd.isna(value):
            return fallback
        text = str(value).strip()
        return text or fallback

    raw_job_title = _clean(job_data.get("job_title") or job_data.get("title"), "Untitled role")
    raw_company = _clean(job_data.get("company"), "Unknown company")
    job_title = escape(raw_job_title)
    company = escape(raw_company)
    location = escape(_clean(job_data.get("location"), "Location not specified"))
    employment_type = escape(_clean(job_data.get("employment_type") or job_data.get("job_type"), "Full-time"))
    salary = escape(_clean(job_data.get("salary_range") or job_data.get("salary"), "Not disclosed"))
    experience = escape(_clean(job_data.get("experience_level") or job_data.get("level"), "All levels"))
    start_date = escape(_clean(job_data.get("start_date"), "Immediate"))
    end_date = escape(_clean(job_data.get("end_date"), "Open until filled"))

    overview, bullets = _derive_job_highlights(job_data.get("job_desc"))
    overview_html = f"<p>{escape(overview)}</p>" if overview else ""

    responsibilities = [escape(item) for item in bullets[:4]]
    preferred = [escape(item) for item in bullets[4:8]]

    responsibilities_html = (
        "<ul class='detail-list'>" + "".join(f"<li>{item}</li>" for item in responsibilities) + "</ul>"
        if responsibilities
        else "<div class='empty-copy'>Responsibilities will be shared soon.</div>"
    )

    preferred_html = (
        "<ul class='detail-list'>" + "".join(f"<li>{item}</li>" for item in preferred) + "</ul>"
        if preferred
        else "<div class='empty-copy'>Preferred qualifications will be updated shortly.</div>"
    )

    qualification_tags = _render_tags(_safe_split(job_data.get("proj_quals", "")))
    if not qualification_tags:
        qualification_tags = "<div class='empty-copy'>This role has no specific skills listed yet.</div>"

    match_score = job_data.get("score")
    if pd.notna(match_score):
        try:
            match_value = float(match_score) * 100 if float(match_score) <= 1 else float(match_score)
            match_display = f"{match_value:.0f}%"
        except (TypeError, ValueError):
            match_display = "—"
    else:
        match_display = "—"

    benefits = [
        "Competitive compensation package",
        "Flexible work arrangements and remote-friendly culture",
        "Comprehensive health and wellness benefits",
    ]
    benefits_html = "<ul class='detail-list'>" + "".join(f"<li>{escape(item)}</li>" for item in benefits) + "</ul>"

    about_team = f"Join {company} to collaborate with a cross-functional team focused on delivering impactful digital experiences."
    contact_domain = re.sub(r"[^a-z0-9]", "", raw_company.lower()) or "company"

    detail_html = f"""
    <div class="job-detail-wrapper">
        <div class="job-detail-main">
            <article class="detail-card">
                <header class="detail-header">
                    <h2>{job_title}</h2>
                    <p>{company} • {location} • {employment_type}</p>
                </header>
                <section class="detail-section">
                    <h3>Job Overview</h3>
                    {overview_html}
                </section>
                <section class="detail-section">
                    <h3>Job Responsibilities</h3>
                    {responsibilities_html}
                </section>
                <section class="detail-section">
                    <h3>Required Skills &amp; Qualifications</h3>
                    <div class="tag-list">{qualification_tags}</div>
                </section>
                <section class="detail-section">
                    <h3>Preferred Qualifications</h3>
                    {preferred_html}
                </section>
                <section class="detail-section">
                    <h3>What We Offer</h3>
                    {benefits_html}
                </section>
                <section class="detail-section">
                    <h3>About the Team</h3>
                    <p>{about_team}</p>
                </section>
            </article>
        </div>
        <aside class="job-detail-sidebar">
            <div class="job-summary-card">
                <div class="summary-group">
                    <span class="summary-label">Location</span>
                    <span class="summary-value">{location}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Employment type</span>
                    <span class="summary-value">{employment_type}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Experience level</span>
                    <span class="summary-value">{experience}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Salary range</span>
                    <span class="summary-value">{salary}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Start date</span>
                    <span class="summary-value">{start_date}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Closing date</span>
                    <span class="summary-value">{end_date}</span>
                </div>
                <div class="summary-group highlight">
                    <span class="summary-label">Your match score</span>
                    <span class="summary-value score">{match_display}</span>
                </div>
                <button class="apply-button" type="button">Apply now</button>
            </div>
            <div class="sidebar-card">
                <h4>Recruiter information</h4>
                <p class="sidebar-text">Have questions? Reach out to the talent team for more details about the role and interview process.</p>
                <div class="contact-chip">talent@{contact_domain}.com</div>
            </div>
        </aside>
    </div>
    """

    st.markdown(detail_html, unsafe_allow_html=True)


def _format_hours(hours: Optional[float]) -> str:
    if hours is None:
        return "—"
    if hours < 1:
        minutes = int(round(hours * 60))
        return f"{minutes} min"
    if hours.is_integer():
        return f"{int(hours)} h"
    return f"{hours:.1f} h"


def _format_rating(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{value:.1f} / 5"


def _coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _estimate_span(hours: Optional[float]) -> int:
    if hours is None or hours <= 0:
        return 2
    weeks = hours / 8.0
    span = int(round(weeks))
    return max(2, min(span, 6))


def _prepare_home_modules(recs_df: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
    modules: List[Dict[str, Any]] = []
    seen_titles = set()
    if recs_df is not None and not recs_df.empty:
        module_position = 0
        for record in recs_df.to_dict(orient="records"):
            title = (
                record.get("course_name")
                or record.get("course_title")
                or f"Learning module {len(modules) + 1}"
            )
            normalized_title = re.sub(r"\s+", " ", str(title)).strip().lower()
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)

            module_position += 1
            duration = _coerce_float(record.get("duration_hours"))

            raw_match = _coerce_float(record.get("score"))
            if raw_match is None:
                match_pct = 0.0
            elif raw_match > 1.0:
                match_pct = max(0.0, min(raw_match, 100.0))
            else:
                match_pct = max(0.0, min(raw_match * 100.0, 100.0))

            raw_progress_candidates = [
                record.get("progress"),
                record.get("completion_rate"),
                record.get("completion_percentage"),
                record.get("progress_percent"),
            ]
            progress_pct: Optional[float] = None
            for candidate in raw_progress_candidates:
                value = _coerce_float(candidate)
                if value is None:
                    continue
                progress_pct = value * 100.0 if 0.0 <= value <= 1.0 else value
                break
            if progress_pct is None:
                progress_pct = min(92.0, 35.0 + (module_position - 1) * 9.0)
            progress_pct = max(0.0, min(progress_pct, 100.0))

            visibility_value = _coerce_float(record.get("visibility"))
            if visibility_value is None:
                visibility_value = max(65.0, progress_pct + 8.0)

            modules.append(
                {
                    "title": title,
                    "provider": record.get("provider") or "—",
                    "duration": duration,
                    "score": match_pct,
                    "visibility": min(100.0, visibility_value),
                    "progress": progress_pct,
                }
            )

    if not modules:
        modules = [module.copy() for module in _FALLBACK_HOME_MODULES]
    elif len(modules) < 6:
        for fallback in _FALLBACK_HOME_MODULES:
            if len(modules) >= 6:
                break
            normalized_title = re.sub(r"\s+", " ", str(fallback.get("title", ""))).strip().lower()
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)
            modules.append(fallback.copy())

    return modules[:6]


def show_home_dashboard(user_id: str, recs_df: Optional[pd.DataFrame]) -> None:
    modules = _prepare_home_modules(recs_df)
    months = ["September", "October", "November", "December"]

    month_header = "".join(
        dedent(
            f"""
            <div class="timeline-month" style="grid-column: {idx * 4 + 1} / span 4;">
                <span class="month-name">{month}</span>
                <div class="month-weeks"><span>W1</span><span>W2</span><span>W3</span><span>W4</span></div>
            </div>
            """
        ).strip()
        for idx, month in enumerate(months)
    )

    timeline_rows: List[str] = []
    start_column = 1
    for idx, module in enumerate(modules, start=1):
        span = _estimate_span(_coerce_float(module.get("duration")))
        if start_column + span > 17:
            start_column = 1
        title = escape(str(module.get("title", f"Module {idx}")))
        provider = escape(str(module.get("provider", "—")))
        duration_display = _format_hours(_coerce_float(module.get("duration")))
        timeline_rows.append(
            dedent(
                f"""
                <div class="timeline-row">
                    <div class="timeline-label">
                        <span class="timeline-eyebrow">Path module {idx}</span>
                        <span class="timeline-title">{title}</span>
                        <span class="timeline-provider">{provider} • {duration_display}</span>
                    </div>
                    <div class="timeline-track">
                        <div class="timeline-bar" style="grid-column: {start_column} / span {span};">
                            <span>{title}</span>
                        </div>
                    </div>
                </div>
                """
            ).strip()
        )
        start_column += span

    progress_rows: List[str] = []
    for idx, module in enumerate(modules, start=1):
        progress_value = _coerce_float(module.get("progress")) or 0.0
        visibility = _coerce_float(module.get("visibility")) or (progress_value + 12.0)
        progress_display = max(0.0, min(progress_value, 100.0))
        visibility_display = int(round(max(0.0, min(visibility, 100.0))))
        progress_rows.append(
            dedent(
                f"""
                <div class="progress-row">
                    <div class="progress-info">
                        <span class="progress-name">{escape(str(module.get('title', f'Module {idx}')))}</span>
                        <span class="progress-provider">{escape(str(module.get('provider', '—')))}</span>
                    </div>
                    <div class="progress-meter">
                        <div class="progress-fill" style="width: {progress_display:.0f}%;"></div>
                    </div>
                    <div class="progress-value">{progress_display:.0f}%</div>
                    <div class="progress-visibility">{visibility_display}% visibility</div>
                </div>
                """
            ).strip()
        )

    dashboard_html = dedent(
        f"""
        <section class="home-dashboard">
            <header class="home-header">
                <div class="home-header-copy">
                    <h2>Growth planner</h2>
                    <p>Visualise your personalised learning path after logging in.</p>
                </div>
                <div class="home-header-search">
                    <span class="search-icon"></span>
                    <input type="text" placeholder="Search planner" />
                </div>
                <div class="home-header-chip">
                    <span class="chip-label">User</span>
                    <span class="chip-value">{escape(user_id)}</span>
                </div>
            </header>
            <div class="home-grid">
                <article class="timeline-card card">
                    <div class="card-header">
                        <div>
                            <h3>Timeline view</h3>
                            <p class="card-subtitle">Track how each recommended module stacks across the upcoming months.</p>
                        </div>
                        <div class="timeline-legend">
                            <span class="legend-pill">In progress</span>
                            <span class="legend-pill upcoming">Upcoming</span>
                        </div>
                    </div>
                    <div class="timeline-month-header">{month_header}</div>
                    <div class="timeline-list">{''.join(timeline_rows)}</div>
                </article>
                <article class="progress-card card">
                    <div class="card-header">
                        <div>
                            <h3>Progress tracking</h3>
                            <p class="card-subtitle">Monitor completion velocity and visibility across your modules.</p>
                        </div>
                        <button type="button" class="ghost-button small">View details</button>
                    </div>
                    <div class="progress-list">{''.join(progress_rows)}</div>
                </article>
            </div>
        </section>
        """
    ).strip()

    st.markdown(dashboard_html, unsafe_allow_html=True)


def show_course_cards(recs_df: pd.DataFrame) -> None:
    """Render learning recommendations using the refreshed learning path layout."""

    if recs_df is None or recs_df.empty:
        return

    scores = (
        pd.to_numeric(recs_df.get("score", pd.Series(dtype=float)), errors="coerce")
        .fillna(0.0)
    )
    durations = pd.to_numeric(
        recs_df.get("duration_hours", pd.Series(dtype=float)), errors="coerce"
    )

    total_courses = int(len(recs_df))
    total_hours = float(durations.dropna().sum()) if not durations.empty else 0.0
    avg_match = float(scores.mean()) * 100 if not scores.empty else 0.0

    skill_counter: Counter[str] = Counter()
    for value in recs_df.get("skills_taught", []):
        for skill in _safe_split(value):
            skill_counter[skill] += 1
    top_skills = [skill for skill, _ in skill_counter.most_common(3)]

    hero_skills = (
        "".join(f"<span class='hero-chip'>{escape(skill)}</span>" for skill in top_skills)
        if top_skills
        else "<span class='hero-chip muted'>Skills will appear here</span>"
    )

    hero_html = dedent(
        f"""
        <section class="learning-hero" id="learning-path">
            <div class="hero-copy">
                <p class="hero-eyebrow">Guided learning journey</p>
                <h2>My Learning Path</h2>
                <p class="hero-description">Focus on these courses to close the most important skill gaps identified in your profile.</p>
                <div class="hero-chip-row">{hero_skills}</div>
            </div>
            <div class="hero-metrics">
                <div class="hero-metric">
                    <span class="metric-label">Courses recommended</span>
                    <span class="metric-value">{total_courses}</span>
                    <span class="metric-caption">Personalised for you</span>
                </div>
                <div class="hero-metric">
                    <span class="metric-label">Estimated effort</span>
                    <span class="metric-value">{_format_hours(total_hours)}</span>
                    <span class="metric-caption">Across all courses</span>
                </div>
                <div class="hero-metric">
                    <span class="metric-label">Average match</span>
                    <span class="metric-value">{avg_match:.0f}%</span>
                    <span class="metric-caption">Alignment to your target role</span>
                </div>
            </div>
        </section>
        """
    ).strip()

    st.markdown(hero_html, unsafe_allow_html=True)

    cards: List[str] = []
    for index, course in enumerate(recs_df.to_dict(orient="records"), start=1):
        taught = _render_tags(_safe_split(course.get("skills_taught", "")))
        score = 0.0
        raw_score = course.get("score")
        try:
            score = float(raw_score) * 100
        except (TypeError, ValueError):
            score = 0.0

        try:
            duration_val = float(course.get("duration_hours"))
        except (TypeError, ValueError):
            duration_val = None

        try:
            rating_val = float(course.get("rating"))
        except (TypeError, ValueError):
            rating_val = None

        provider = str(course.get("provider") or "Unknown provider")
        difficulty = str(
            course.get("difficulty_level")
            or course.get("difficulty")
            or "—"
        )
        summary_copy = str(
            course.get(
                "course_summary",
                "Designed to strengthen this capability based on your current readiness levels.",
            )
        )

        cards.append(
            dedent(
                f"""
                <article class="learning-card">
                    <div class="learning-card-header">
                        <div class="learning-card-title">
                            <span class="card-eyebrow">Path module {index}</span>
                            <h3>{course.get('course_name', 'Untitled course')}</h3>
                            <p class="card-meta">{escape(provider)} • {escape(str(difficulty))}</p>
                        </div>
                        <div class="learning-card-progress">
                            <span class="progress-label">Match alignment</span>
                            <div class="progress-track">
                                <div class="progress-fill" style="width: {min(max(score, 0.0), 100.0):.0f}%"></div>
                            </div>
                            <span class="progress-value">{score:.0f}%</span>
                        </div>
                    </div>
                    <p class="learning-card-description">{escape(summary_copy)}</p>
                    <div class="learning-card-grid">
                        <div class="grid-item">
                            <span class="grid-label">Duration</span>
                            <span class="grid-value">{_format_hours(duration_val)}</span>
                        </div>
                        <div class="grid-item">
                            <span class="grid-label">Difficulty</span>
                            <span class="grid-value">{escape(str(difficulty))}</span>
                        </div>
                        <div class="grid-item">
                            <span class="grid-label">Provider</span>
                            <span class="grid-value">{escape(provider)}</span>
                        </div>
                        <div class="grid-item">
                            <span class="grid-label">Rating</span>
                            <span class="grid-value">{_format_rating(rating_val)}</span>
                        </div>
                    </div>
                    <div class="learning-card-skills">
                        <span class="grid-label">Skills you'll build</span>
                        <div class="tag-list">{taught or '<span class="pill muted">Skill data unavailable</span>'}</div>
                    </div>
                    <div class="learning-card-actions">
                        <button type="button" class="ghost-button">Add to planner</button>
                        <button type="button" class="primary-button">Continue</button>
                    </div>
                </article>
                """
            ).strip()
        )

    st.markdown(
        f"<section class='learning-path-list'>{''.join(cards)}</section>",
        unsafe_allow_html=True,
    )

def load_model():
    """
    Load serialized model data (MiniLM recommender .pkl)
    Expected keys:
        - employee_df
        - job_df
        - course_df
        - merged
        - recommendations
    """
    data = joblib.load("/Users/minhtan/Documents/GitHub/RecommendationSystem/final/models/minilm_recommender_light.pkl")
    return data

def get_user_info(data, user_id):
    emp_df = data.get("employee_df", pd.DataFrame())
    info = emp_df[emp_df["user_id"] == user_id]
    return info.to_dict(orient="records")[0] if not info.empty else None

def top_jobs_for_user(data, user_id, n=5):
    merged = data.get("merged", pd.DataFrame())
    if merged.empty:
        return pd.DataFrame()

    subset = merged[merged["user_id"] == user_id].copy()

    job_df = data.get("job_df", pd.DataFrame())
    if not job_df.empty and "jid" in job_df.columns:
        # keep only relevant job columns to avoid duplicating heavy text fields
        optional_columns = [
            "job_title",
            "title",
            "location",
            "company",
            "employment_type",
            "job_type",
            "salary_range",
            "salary",
            "experience_level",
            "level",
            "job_desc",
            "start_date",
            "end_date",
        ]
        job_columns = ["jid"] + [col for col in optional_columns if col in job_df.columns]
        job_details = job_df[job_columns].drop_duplicates(subset=["jid"])
        subset = subset.merge(job_details, on="jid", how="left")

    if "job_title" not in subset.columns:
        if "title" in subset.columns:
            subset = subset.rename(columns={"title": "job_title"})
        else:
            if not job_df.empty and "jid" in job_df.columns:
                title_column = "job_title" if "job_title" in job_df.columns else None
                if not title_column and "title" in job_df.columns:
                    title_column = "title"
                if title_column:
                    title_map = job_df.set_index("jid")[title_column]
                    subset["job_title"] = subset["jid"].map(title_map)
        if "job_title" not in subset.columns:
            subset["job_title"] = subset["jid"]

    if "score" in subset.columns:
        subset = subset.sort_values(by="score", ascending=False, na_position="last")

    if "jid" in subset.columns:
        subset = subset.drop_duplicates(subset=["jid"], keep="first")

    desired_order = [
        "jid",
        "job_title",
        "proj_quals",
        "location",
        "company",
        "employment_type",
        "job_type",
        "salary_range",
        "salary",
        "experience_level",
        "level",
        "job_desc",
        "start_date",
        "end_date",
        "score",
    ]
    combined = subset.copy()

    final_columns = [col for col in desired_order if col in combined.columns]
    if not final_columns:
        return pd.DataFrame()

    return combined[final_columns].head(n)

def recommend_for_user(data, user_id):
    recs = data.get("recommendations", {})
    if user_id not in recs:
        return pd.DataFrame()
    df = pd.DataFrame(recs[user_id])
    df["score"] = df["score"].astype(float)
    return df.sort_values(by="score", ascending=False)

st.set_page_config(page_title="SkillGraph System", layout="wide")

# Apply global style
apply_custom_style()

st.title("SkillGraph Recommender System")
st.caption("Discover tailored job matches and courses designed around your strengths.")

@st.cache_resource
def init_model():
    return load_model()

data = init_model()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None

if "job_click_nonce" not in st.session_state:
    st.session_state.job_click_nonce = None

if not st.session_state.user_id:
    st.markdown("<h3 class='centered-text'>Login to your account</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="empty-state">Enter your employee ID to see personalised insights.</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.25, 0.5, 0.25])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            user_id = st.text_input("User ID", placeholder="e.g. U0001", max_chars=20)
            submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if user_id and user_id in data["employee_df"]["user_id"].values:
            st.session_state.user_id = user_id
            st.session_state.selected_job_id = None
            st.session_state.job_click_nonce = None
            st.success(f"Welcome back, {user_id}! Redirecting...")
            st.rerun()
        else:
            st.error("We couldn't find that ID. Please check and try again.")
    st.stop()

col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.selected_job_id = None
        st.session_state.job_click_nonce = None
        st.rerun()

user_id = st.session_state.user_id
st.markdown(f"### Hello, {user_id}!")
st.info(
    "Explore the tabs below to review your profile, discover matching roles, and close any skill gaps with curated courses."
)

recommendations = recommend_for_user(data, user_id)

tabs = st.tabs(["Home", "Profile", "Job Match", "Learning Path"])

with tabs[0]:
    show_home_dashboard(user_id, recommendations)

with tabs[1]:
    st.subheader("Your Profile")
    user = get_user_info(data, user_id)
    if user is not None:
        show_profile_card(user)
    else:
        st.warning("User not found in dataset.")

with tabs[2]:
    st.markdown(
        """
        <section class="job-match-hero" id="job-match">
            <div class="job-hero-copy">
                <h2>Find Job</h2>
                <p>Discover curated opportunities that align with your strengths and aspirations.</p>
            </div>
            <div class="job-filter-bar">
                <div class="filter-field wide">
                    <label>Search</label>
                    <div class="input-shell">
                        <span class="input-icon"></span>
                        <input type="text" placeholder="Search job title or keyword" />
                    </div>
                </div>
                <div class="filter-field">
                    <label>Location</label>
                    <div class="input-shell">
                        <select>
                            <option selected>All locations</option>
                            <option>Remote</option>
                            <option>On-site</option>
                        </select>
                    </div>
                </div>
                <div class="filter-field">
                    <label>Job type</label>
                    <div class="input-shell">
                        <select>
                            <option selected>Any type</option>
                            <option>Full-time</option>
                            <option>Part-time</option>
                            <option>Contract</option>
                        </select>
                    </div>
                </div>
                <div class="filter-field">
                    <label>Salary range</label>
                    <div class="input-shell">
                        <select>
                            <option selected>All ranges</option>
                            <option>Up to $60k</option>
                            <option>$60k - $90k</option>
                            <option>$90k - $120k</option>
                            <option>$120k+</option>
                        </select>
                    </div>
                </div>
                <button type="button" class="filter-button">Search</button>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    jobs = top_jobs_for_user(data, user_id, n=6)
    if jobs is not None and not jobs.empty:
        selected_job_id = st.session_state.get("selected_job_id")
        selected_row = None

        if selected_job_id is not None:
            resolved_id = str(selected_job_id)
            for key in ("jid", "job_id", "id"):
                if key in jobs.columns:
                    matches = jobs[jobs[key].astype(str) == resolved_id]
                    if not matches.empty:
                        selected_row = matches.iloc[0]
                        break

            if selected_row is None:
                st.session_state.selected_job_id = None
                selected_job_id = None

        if selected_job_id is None:
            st.markdown(
                f"""
                <div class="job-results-header">
                    <div>
                        <h3>Job match</h3>
                        <p>Based on your profile data</p>
                    </div>
                    <span class="results-count">{len(jobs)} roles available</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            previous_selection = st.session_state.get("selected_job_id")
            show_job_cards(jobs)
            if st.session_state.get("selected_job_id") is not None and (
                st.session_state.get("selected_job_id") != previous_selection
            ):
                st.rerun()
        else:
            back_col, _ = st.columns([0.2, 0.8])
            with back_col:
                if st.button("← Back to job list", use_container_width=True):
                    st.session_state["selected_job_id"] = None
                    st.session_state["job_click_nonce"] = None
                    st.rerun()

            show_job_detail(selected_row)
    else:
        st.session_state.selected_job_id = None
        st.session_state.job_click_nonce = None
        st.info("No job match data available for this user.")

with tabs[3]:
    if recommendations is not None and not recommendations.empty:
        show_course_cards(recommendations)
    else:
        st.info("No learning recommendations available yet.")
