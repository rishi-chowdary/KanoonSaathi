package com.lexilegal.service;

import com.lexilegal.exception.InvalidFileException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.UUID;

@Service
public class DocumentStorageService {

    private final Path uploadDir;
    private final long maxSizeBytes;

    public DocumentStorageService(
            @Value("${app.storage.upload-dir:./uploads}") String uploadDirPath,
            @Value("${app.storage.max-file-size-mb:10}") long maxFileSizeMb) {
        this.uploadDir = Paths.get(uploadDirPath).toAbsolutePath().normalize();
        this.maxSizeBytes = maxFileSizeMb * 1024 * 1024;
        try {
            Files.createDirectories(this.uploadDir);
        } catch (IOException e) {
            throw new RuntimeException("could not initialize upload directory: " + uploadDirPath, e);
        }
    }

    public void validate(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new InvalidFileException("file cannot be empty");
        }

        if (file.getSize() > maxSizeBytes) {
            throw new InvalidFileException("file exceeds maximum allowed size of 10MB");
        }

        String originalName = file.getOriginalFilename();
        if (originalName == null || !originalName.contains(".")) {
            throw new InvalidFileException("file must have a valid extension (.pdf, .docx, .txt)");
        }

        String ext = getExtension(originalName).toLowerCase();
        if (!ext.equals("pdf") && !ext.equals("docx") && !ext.equals("txt")) {
            throw new InvalidFileException("unsupported file extension; only .pdf, .docx, and .txt files are supported");
        }

        try (InputStream is = file.getInputStream()) {
            byte[] header = new byte[8];
            int read = is.read(header);
            if (read < 4) {
                throw new InvalidFileException("file is too small or empty");
            }

            // Check executable header (MZ DOS header or ELF header)
            if ((header[0] == 0x4D && header[1] == 0x5A) ||
                (header[0] == 0x7F && header[1] == 0x45 && header[2] == 0x4C && header[3] == 0x46)) {
                throw new InvalidFileException("executable files are not allowed");
            }

            if (ext.equals("pdf")) {
                // PDF magic bytes: %PDF- (0x25 0x50 0x44 0x46 0x2D)
                if (header[0] != 0x25 || header[1] != 0x50 || header[2] != 0x44 || header[3] != 0x46) {
                    throw new InvalidFileException("file content does not match declared PDF format");
                }
            } else if (ext.equals("docx")) {
                // DOCX is a zip archive: PK\x03\x04 (0x50 0x4B 0x03 0x04)
                if (header[0] != 0x50 || header[1] != 0x4B || header[2] != 0x03 || header[3] != 0x04) {
                    throw new InvalidFileException("file content does not match declared DOCX format");
                }
            } else if (ext.equals("txt")) {
                // Check that first 512 bytes don't contain null characters
                byte[] sample = file.getBytes();
                int checkLen = Math.min(sample.length, 512);
                for (int i = 0; i < checkLen; i++) {
                    if (sample[i] == 0x00) {
                        throw new InvalidFileException("file content contains binary data and is not a valid text file");
                    }
                }
            }
        } catch (IOException e) {
            throw new InvalidFileException("could not read file content: " + e.getMessage());
        }
    }

    public String computeSha256(MultipartFile file) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(file.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException | IOException e) {
            throw new RuntimeException("failed to compute file hash", e);
        }
    }

    public Path store(MultipartFile file) {
        String originalName = file.getOriginalFilename();
        String ext = getExtension(originalName);
        String randomizedName = UUID.randomUUID() + "." + ext;
        Path targetPath = this.uploadDir.resolve(randomizedName).normalize();

        try (InputStream is = file.getInputStream()) {
            Files.copy(is, targetPath, StandardCopyOption.REPLACE_EXISTING);
            return targetPath;
        } catch (IOException e) {
            throw new RuntimeException("failed to store file on disk", e);
        }
    }

    public void deleteFile(String storagePath) {
        if (storagePath == null || storagePath.isBlank()) {
            return;
        }
        try {
            Path path = Paths.get(storagePath);
            Files.deleteIfExists(path);
        } catch (IOException ignored) {
        }
    }

    private String getExtension(String filename) {
        int idx = filename.lastIndexOf('.');
        return (idx > 0 && idx < filename.length() - 1) ? filename.substring(idx + 1) : "";
    }
}
