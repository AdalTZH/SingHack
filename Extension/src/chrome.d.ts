// Chrome Extension API Type Definitions
// These types are available in the Chrome extension runtime environment

interface ChromeRuntimeMessage {
  type: string;
  [key: string]: any;
}

interface ChromeMessageSender {
  tab?: any;
  frameId?: number;
  id?: string;
  url?: string;
}

declare const chrome: {
  runtime: {
    sendMessage(message: ChromeRuntimeMessage): Promise<any>;
    onMessage: {
      addListener(
        callback: (
          message: ChromeRuntimeMessage,
          sender: ChromeMessageSender,
          sendResponse: (response?: any) => void
        ) => void | boolean
      ): void;
    };
  };
  storage: {
    sync: {
      get(keys?: string | string[] | { [key: string]: any } | null): Promise<{ [key: string]: any }>;
      set(items: { [key: string]: any }): Promise<void>;
    };
  };
  tabs: {
    query(queryInfo: { active?: boolean; currentWindow?: boolean }): Promise<any[]>;
    get(tabId: number): Promise<any>;
  };
  sidePanel: {
    open(options: { tabId?: number }): Promise<void>;
  };
  action: {
    onClicked: {
      addListener(callback: (tab: any) => void): void;
    };
  };
};
