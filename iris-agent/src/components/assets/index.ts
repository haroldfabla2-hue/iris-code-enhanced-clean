// Assets Components - Export all asset-related components
export { default as AssetManager } from './AssetManager';
export { default as AssetGenerator } from './AssetGenerator';
export { default as AssetChat } from './AssetChat';
export { default as AssetHistory } from './AssetHistory';

// Types (re-export from lib/api)
export type {
  AssetGenerationRequest,
  AssetResponse,
  AssetCategoryResponse,
  AssetChatMessage,
  AssetChatResponse,
  AssetFile,
  FreepikConfig
} from '../../lib/api';