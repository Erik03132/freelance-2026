import { RawJob } from '../adapters/base';
/**
 * Тип ответа заказчику
 */
export interface ClientResponse {
    type: 'code' | 'lecture' | 'text' | 'design' | 'data';
    subject: string;
    letter: string;
    sample: string;
    explanation: string;
    nextSteps: string[];
}
/**
 * Генератор персонализированных ответов
 */
export declare class ResponseGenerator {
    /**
     * Определить тип задачи по описанию
     */
    detectTaskType(job: RawJob): ClientResponse['type'];
    /**
     * Сгенерировать ответ для заказчика
     */
    generate(job: RawJob, skills?: string[]): ClientResponse;
    /**
     * Генерация ответа для учебных задач (лекции, курсы)
     */
    private generateLectureResponse;
    /**
     * Генерация фрагмента лекции
     */
    private generateLectureSample;
    /**
     * Генерация ответа для задач по коду
     */
    private generateCodeResponse;
    /**
     * Генерация ответа для текстовых задач
     */
    private generateTextResponse;
    /**
     * Генерация ответа для дизайн-задач
     */
    private generateDesignResponse;
    /**
     * Генерация ответа для задач по данным
     */
    private generateDataResponse;
}
//# sourceMappingURL=response.d.ts.map