#!/bin/bash
.PHONY: server


server:
	cd server && uvicorn main:app --reload --host 0.0.0.0 --port 4100
