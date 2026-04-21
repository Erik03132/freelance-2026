"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CloudStorageService = void 0;
/**
 * Сервис для загрузки файлов в облако (например, для 30% CORE артефактов)
 * Использует нативный fetch для минимизации зависимостей
 */
class CloudStorageService {
    /**
     * Анонимная загрузка файла на 0x0.st
     */
    static async uploadFile(buffer, filename) {
        try {
            const formData = new FormData();
            // Конвертируем Buffer в Uint8Array для совместимости с native Blob/fetch
            const blob = new Blob([new Uint8Array(buffer)]);
            formData.append('file', blob, filename);
            const response = await fetch('https://0x0.st', {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                return (await response.text()).trim();
            }
            throw new Error(`Failed to upload: ${response.statusText}`);
        }
        catch (error) {
            console.error('Cloud upload error:', error);
            return this.uploadToImgBB(buffer);
        }
    }
    /**
     * Загрузка на ImgBB
     */
    static async uploadToImgBB(buffer) {
        try {
            const apiKey = process.env.IMGBB_API_KEY || 'e37435f3083ec0f7d54baf19f076e0d4';
            const formData = new URLSearchParams();
            formData.append('image', buffer.toString('base64'));
            const response = await fetch(`https://api.imgbb.com/1/upload?key=${apiKey}`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (data.success && data.data && data.data.url) {
                return data.data.url;
            }
            throw new Error('Invalid ImgBB response');
        }
        catch (error) {
            console.error('ImgBB upload error:', error);
            throw error;
        }
    }
}
exports.CloudStorageService = CloudStorageService;
