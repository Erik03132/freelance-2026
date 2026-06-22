export interface Message {
  role: 'user' | 'bot';
  text: string;
}

export interface ChatState {
  messages: Message[];
  input: string;
  loading: boolean;
  isOpen: boolean;
}
