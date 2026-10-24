import '../app.css';
import { mount } from 'svelte';
import ReportPage from '#lib/report-page.svelte';

mount(ReportPage, { target: document.getElementById('app')! });
