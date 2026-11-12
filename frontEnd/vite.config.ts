import adapter from '@sveltejs/adapter-auto';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

const libPath = decodeURIComponent(new URL('./src/lib', import.meta.url).pathname).replace(
	/^\/([A-Za-z]:)/,
	'$1'
);

export default defineConfig({
	resolve: {
		alias: {
			$lib: libPath
		}
	},
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		})
	]
});
