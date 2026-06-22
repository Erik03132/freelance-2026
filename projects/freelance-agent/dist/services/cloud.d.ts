/**
 * Сервис для загрузки файлов в облако (например, для 30% CORE артефактов)
 * Использует нативный fetch для минимизации зависимостей
 */
export declare class CloudStorageService {
    /**
     * Анонимная загрузка файла на 0x0.st
     */
    static uploadFile(buffer: Buffer, filename: string): Promise<string>;
    /**
     * Загрузка на ImgBB
     */
    static uploadToImgBB(buffer: Buffer): Promise<string>;
}
//# sourceMappingURL=cloud.d.ts.map