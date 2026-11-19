package com.taeun.crop.diagnosis;

import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;

public record ImageFile(Resource resource, MediaType mediaType) {
}
