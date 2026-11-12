import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const rootDir = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
	tsconfig: resolve(rootDir, 'tests/tsconfig.json'),
	resolve: {
		alias: {
			$lib: resolve(rootDir, 'src/lib')
		}
	},
	test: {
		environment: 'node',
		include: ['tests/unit/**/*.test.ts'],
		clearMocks: true,
		restoreMocks: true
	}
});
