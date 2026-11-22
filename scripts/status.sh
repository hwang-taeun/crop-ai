#!/bin/bash
# 세 서버가 켜져 있는지 확인
ss -ltn | grep -q ':8000' && echo "① AI 서버     : 켜짐" || echo "① AI 서버     : 꺼짐"
ss -ltn | grep -q ':8080' && echo "② Spring 서버 : 켜짐" || echo "② Spring 서버 : 꺼짐"
ss -ltn | grep -q ':5173' && echo "③ React 화면  : 켜짐" || echo "③ React 화면  : 꺼짐"
ss -ltn | grep -q ':3306' && echo "   MySQL       : 켜짐" || echo "   MySQL       : 꺼짐 → sudo service mysql start"
