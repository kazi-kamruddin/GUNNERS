import adapterAuto from '@sveltejs/adapter-auto';
import adapterVercel from '@sveltejs/adapter-vercel';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

const nodeProcess = (
	globalThis as { process?: { env?: Record<string, string | undefined>; platform?: string } }
).process;
const adapter =
	nodeProcess?.env?.VERCEL || nodeProcess?.platform !== 'win32' ? adapterVercel : adapterAuto;

const libPath = decodeURIComponent(new URL('./src/lib', import.meta.url).pathname).replace(
	/^\/([A-Za-z]:)/,
	'$1'
);

export default defineConfig({
	envPrefix: ['VITE_', 'PUBLIC_'],
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
