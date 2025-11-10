// Memory Components - Export all memory-related components
export { default as MemoryManager } from './MemoryManager';

// Types (re-export from lib/api)
export type {
  MemorySearchRequest,
  MemorySearchResponse,
  MemoryStoreRequest,
  MemoryStoreResponse,
  MemoryStatsResponse,
  StoreDocumentRequest,
  MemoryClearRequest,
  MemoryClearResponse,
  MemorySearchResult
} from '../../lib/api';