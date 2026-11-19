package com.taeun.crop.ai;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.Crop;
import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.storage.ImageType;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

/** Spring → FastAPI AI 서버 호출 (docs/api-spec.md 7장) */
@Component
public class AiClient {

    private static final Logger log = LoggerFactory.getLogger(AiClient.class);

    private final RestClient client;
    private final String token;

    public AiClient(@Value("${app.ai.base-url}") String baseUrl,
                    @Value("${app.ai.token}") String token,
                    @Value("${app.ai.timeout-seconds}") int timeoutSeconds) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(3));
        factory.setReadTimeout(Duration.ofSeconds(timeoutSeconds));
        this.client = RestClient.builder().baseUrl(baseUrl).requestFactory(factory).build();
        this.token = token;
        if (token == null || token.isBlank()) {
            log.warn("INTERNAL_TOKEN 이 비어 있습니다. AI 서버도 토큰 없이 실행 중일 때만 동작합니다 (개발용).");
        }
    }

    public AiPredictResponse predict(byte[] image, ImageType type, Crop crop) {
        HttpHeaders partHeaders = new HttpHeaders();
        partHeaders.setContentType(type.mediaType());
        ByteArrayResource file = new ByteArrayResource(image) {
            @Override
            public String getFilename() {
                return "upload." + type.ext();
            }
        };
        MultiValueMap<String, Object> parts = new LinkedMultiValueMap<>();
        parts.add("image", new HttpEntity<>(file, partHeaders));
        parts.add("crop", crop.name());

        try {
            AiPredictResponse res = client.post()
                    .uri("/predict")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .headers(h -> {
                        if (token != null && !token.isBlank()) {
                            h.set("X-Internal-Token", token);
                        }
                    })
                    .body(parts)
                    .retrieve()
                    .body(AiPredictResponse.class);
            if (res == null || res.predictions() == null || res.predictions().isEmpty()) {
                log.error("AI 서버 응답이 비어 있음");
                throw new ApiException(ErrorCode.AI_UNAVAILABLE);
            }
            return res;
        } catch (RestClientResponseException e) {
            int status = e.getStatusCode().value();
            if (status == 400) {
                throw new ApiException(ErrorCode.INVALID_IMAGE, "사진을 읽을 수 없습니다. 다른 사진으로 다시 시도하세요.");
            }
            if (status == 413) {
                throw new ApiException(ErrorCode.IMAGE_TOO_LARGE);
            }
            if (status == 401) {
                log.error("AI 서버 토큰 불일치 — Spring 과 AI 서버의 INTERNAL_TOKEN 을 확인하세요.");
            } else {
                log.error("AI 서버 오류 응답: {} {}", status, e.getResponseBodyAsString());
            }
            throw new ApiException(ErrorCode.AI_UNAVAILABLE);
        } catch (RestClientException e) {
            log.warn("AI 서버 연결 실패: {}", e.getMessage());
            throw new ApiException(ErrorCode.AI_UNAVAILABLE);
        }
    }
}
