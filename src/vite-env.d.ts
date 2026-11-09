/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BHARATCODE_API_KEY: string;
  readonly VITE_BHARATCODE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
