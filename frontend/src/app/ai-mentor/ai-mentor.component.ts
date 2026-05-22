import { Component, inject, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AIMentorService, ChatMessage } from '../services/ai-mentor.service';
import { NotificationService } from '../services/notification.service';

type MentorMode = 'beginner' | 'prelims' | 'mains' | 'quick_revision';

@Component({
  selector: 'app-ai-mentor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">

      <!-- Header -->
      <div class="glass-card p-4 mb-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
               style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">🤖</div>
          <div>
            <h1 class="text-lg font-bold text-white">AI Mentor</h1>
            <p class="text-gray-400 text-xs">Your personal UPSC preparation guide</p>
          </div>
        </div>

        <!-- Mode selector -->
        <div class="flex gap-2">
          @for (mode of modes; track mode.value) {
            <button
              (click)="selectedMode.set(mode.value)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
              [class]="selectedMode() === mode.value
                ? 'text-white border border-primary-500/50'
                : 'text-gray-400 hover:text-white border border-white/10'"
              [style.background]="selectedMode() === mode.value ? mode.color + '20' : 'transparent'"
            >
              {{ mode.icon }} {{ mode.label }}
            </button>
          }
        </div>
      </div>

      <!-- Chat area -->
      <div class="flex-1 glass-card overflow-hidden flex flex-col">

        <!-- Messages -->
        <div #chatContainer class="flex-1 overflow-y-auto p-4 space-y-4">

          <!-- Welcome message -->
          @if (messages().length === 0) {
            <div class="flex flex-col items-center justify-center h-full text-center py-12">
              <div class="text-6xl mb-4">🤖</div>
              <h2 class="text-xl font-bold text-white mb-2">Ask me anything about UPSC</h2>
              <p class="text-gray-400 text-sm mb-6 max-w-md">
                I can explain concepts, analyze PYQ patterns, help with answer writing,
                and link current affairs to static topics.
              </p>

              <!-- Suggested prompts -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                @for (prompt of suggestedPrompts; track prompt) {
                  <button
                    (click)="sendSuggestedPrompt(prompt)"
                    class="text-left p-3 rounded-xl text-sm text-gray-300 hover:text-white transition-all duration-200"
                    style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);"
                  >
                    {{ prompt }}
                  </button>
                }
              </div>
            </div>
          }

          <!-- Chat messages -->
          @for (message of messages(); track $index) {
            <div class="flex gap-3" [class.flex-row-reverse]="message.role === 'user'">
              <!-- Avatar -->
              <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm"
                   [style.background]="message.role === 'user'
                     ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                     : 'linear-gradient(135deg, #10b981, #059669)'">
                {{ message.role === 'user' ? '👤' : '🤖' }}
              </div>

              <!-- Message bubble -->
              <div
                class="max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
                [class]="message.role === 'user'
                  ? 'text-white rounded-tr-sm'
                  : 'text-gray-200 rounded-tl-sm'"
                [style.background]="message.role === 'user'
                  ? 'linear-gradient(135deg, #6366f1, #4f46e5)'
                  : 'rgba(255,255,255,0.05)'"
                [style.border]="message.role === 'assistant' ? '1px solid rgba(255,255,255,0.08)' : 'none'"
              >
                <div [innerHTML]="formatMessage(message.content)"></div>
                <p class="text-xs opacity-50 mt-2">
                  {{ message.timestamp | date:'HH:mm' }}
                </p>
              </div>
            </div>
          }

          <!-- Streaming indicator -->
          @if (isStreaming()) {
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                   style="background: linear-gradient(135deg, #10b981, #059669);">🤖</div>
              <div class="glass-card px-4 py-3 rounded-2xl rounded-tl-sm">
                <div class="flex gap-1">
                  <span class="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style="animation-delay: 0ms"></span>
                  <span class="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style="animation-delay: 150ms"></span>
                  <span class="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style="animation-delay: 300ms"></span>
                </div>
              </div>
            </div>
          }
        </div>

        <!-- Input area -->
        <div class="border-t border-white/5 p-4">
          <div class="flex gap-3">
            <div class="flex-1 relative">
              <textarea
                [(ngModel)]="inputMessage"
                (keydown.enter)="onEnterKey($event)"
                placeholder="Ask about any UPSC topic... (Enter to send, Shift+Enter for new line)"
                rows="2"
                class="input-field resize-none pr-12 text-sm"
                [disabled]="isStreaming()"
              ></textarea>
            </div>
            <button
              (click)="sendMessage()"
              [disabled]="!inputMessage.trim() || isStreaming()"
              class="btn-primary px-4 self-end flex items-center gap-2"
            >
              @if (isStreaming()) {
                <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
              } @else {
                <span>Send</span>
                <span>→</span>
              }
            </button>
          </div>

          <!-- Quick actions -->
          <div class="flex gap-2 mt-2 flex-wrap">
            @for (action of quickActions; track action.label) {
              <button
                (click)="sendSuggestedPrompt(action.prompt)"
                class="text-xs px-3 py-1 rounded-full text-gray-400 hover:text-white transition-all"
                style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);"
              >
                {{ action.icon }} {{ action.label }}
              </button>
            }
          </div>
        </div>
      </div>
    </div>
  `,
})
export class AIMentorComponent implements AfterViewChecked {
  @ViewChild('chatContainer') chatContainer!: ElementRef;

  private mentorService = inject(AIMentorService);
  private notifications = inject(NotificationService);

  messages = signal<ChatMessage[]>([]);
  inputMessage = '';
  isStreaming = signal(false);
  selectedMode = signal<MentorMode>('mains');

  modes = [
    { value: 'beginner' as MentorMode, label: 'Beginner', icon: '🌱', color: '#10b981' },
    { value: 'prelims' as MentorMode, label: 'Prelims', icon: '📋', color: '#3b82f6' },
    { value: 'mains' as MentorMode, label: 'Mains', icon: '✍️', color: '#6366f1' },
    { value: 'quick_revision' as MentorMode, label: 'Quick Rev', icon: '⚡', color: '#f59e0b' },
  ];

  suggestedPrompts = [
    'Explain El Niño and its impact on Indian monsoon',
    'Difference between weathering and erosion',
    'Give answer structure for federalism question',
    'Link climate change with Indian agriculture',
  ];

  quickActions = [
    { icon: '📖', label: 'Explain', prompt: 'Explain ' },
    { icon: '⚖️', label: 'Compare', prompt: 'Compare and contrast ' },
    { icon: '✍️', label: 'Answer Structure', prompt: 'Give answer structure for: ' },
    { icon: '🔗', label: 'Current Affairs Link', prompt: 'Link with current affairs: ' },
    { icon: '📋', label: 'Key Points', prompt: 'Give key points for UPSC on: ' },
  ];

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  onEnterKey(event: Event): void {
    const keyEvent = event as KeyboardEvent;
    if (!keyEvent.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  sendSuggestedPrompt(prompt: string): void {
    this.inputMessage = prompt;
    if (!prompt.endsWith(' ')) {
      this.sendMessage();
    }
  }

  sendMessage(): void {
    const query = this.inputMessage.trim();
    if (!query || this.isStreaming()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    this.messages.update(msgs => [...msgs, userMessage]);
    this.inputMessage = '';
    this.isStreaming.set(true);

    const history = this.messages().slice(-10).map(m => ({
      role: m.role,
      content: m.content,
    }));

    this.mentorService.chat(
      { query, mode: this.selectedMode() },
      history as any,
    ).subscribe({
      next: (res) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: res.response,
          timestamp: new Date(),
        };
        this.messages.update(msgs => [...msgs, assistantMessage]);
        this.isStreaming.set(false);
      },
      error: () => {
        this.isStreaming.set(false);
        this.notifications.error('Failed to get AI response. Please try again.');
      },
    });
  }

  formatMessage(content: string): string {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^## (.*$)/gm, '<h3 class="text-white font-semibold mt-3 mb-1">$1</h3>')
      .replace(/^### (.*$)/gm, '<h4 class="text-gray-200 font-medium mt-2 mb-1">$1</h4>')
      .replace(/^- (.*$)/gm, '<li class="ml-4 list-disc">$1</li>')
      .replace(/\n/g, '<br>');
  }

  private scrollToBottom(): void {
    try {
      const el = this.chatContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    } catch {}
  }
}
