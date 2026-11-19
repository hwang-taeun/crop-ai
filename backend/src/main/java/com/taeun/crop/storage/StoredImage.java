package com.taeun.crop.storage;

/** 저장한 원본·썸네일의 키 (저장 폴더 기준 상대 경로) */
public record StoredImage(String originalKey, String thumbnailKey) {
}
