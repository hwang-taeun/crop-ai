package com.taeun.crop.storage;

import com.taeun.crop.common.ApiException;
import com.taeun.crop.common.ErrorCode;
import com.taeun.crop.common.Times;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.UUID;
import javax.imageio.ImageIO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;

/**
 * 진단 사진을 서버 디스크에 저장.
 * 키 형식: yyyy/MM/<uuid>.jpg|png (원본), yyyy/MM/<uuid>_thumb.jpg (썸네일)
 * 키는 서버가 만들고, 읽을 때도 저장 폴더 밖으로 나가지 못하게 검사함.
 */
@Component
public class ImageStorage {

    private static final Logger log = LoggerFactory.getLogger(ImageStorage.class);
    private static final int THUMB_MAX = 300;
    private static final DateTimeFormatter DIR = DateTimeFormatter.ofPattern("yyyy/MM");

    private final Path base;

    public ImageStorage(@Value("${app.storage.dir}") String dir) {
        this.base = Path.of(dir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(base);
        } catch (IOException e) {
            throw new UncheckedIOException("사진 저장 폴더를 만들 수 없습니다: " + base, e);
        }
        log.info("사진 저장 폴더: {}", base);
    }

    public StoredImage store(byte[] original, ImageType type, BufferedImage image) {
        String sub = LocalDate.now(Times.SEOUL).format(DIR);
        String id = UUID.randomUUID().toString();
        String originalKey = sub + "/" + id + "." + type.ext();
        String thumbKey = sub + "/" + id + "_thumb.jpg";
        try {
            Path o = resolve(originalKey);
            Files.createDirectories(o.getParent());
            Files.write(o, original);
            Files.write(resolve(thumbKey), thumbnail(image));
        } catch (IOException e) {
            deleteQuietly(originalKey, thumbKey);
            throw new UncheckedIOException("사진 저장 실패", e);
        }
        return new StoredImage(originalKey, thumbKey);
    }

    public Resource load(String key) {
        Path p = resolve(key);
        if (!Files.isRegularFile(p)) {
            throw new ApiException(ErrorCode.NOT_FOUND, "사진 파일이 없습니다.");
        }
        return new FileSystemResource(p);
    }

    public void deleteQuietly(String... keys) {
        for (String key : keys) {
            if (key == null) {
                continue;
            }
            try {
                Files.deleteIfExists(resolve(key));
            } catch (IOException | RuntimeException e) {
                log.warn("사진 삭제 실패: {}", key, e);
            }
        }
    }

    private Path resolve(String key) {
        Path p = base.resolve(key).normalize();
        if (!p.startsWith(base)) {
            throw new ApiException(ErrorCode.NOT_FOUND);
        }
        return p;
    }

    /** 긴 변 300px JPEG. 투명 PNG는 흰 배경으로 합성 */
    private static byte[] thumbnail(BufferedImage src) throws IOException {
        int w = src.getWidth();
        int h = src.getHeight();
        double scale = Math.min(1.0, (double) THUMB_MAX / Math.max(w, h));
        int tw = Math.max(1, (int) Math.round(w * scale));
        int th = Math.max(1, (int) Math.round(h * scale));
        BufferedImage t = new BufferedImage(tw, th, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = t.createGraphics();
        try {
            g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
            g.setColor(Color.WHITE);
            g.fillRect(0, 0, tw, th);
            g.drawImage(src, 0, 0, tw, th, null);
        } finally {
            g.dispose();
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ImageIO.write(t, "jpg", out);
        return out.toByteArray();
    }
}
