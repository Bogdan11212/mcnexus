const sidebarContent = `
<div class="space-y-8">
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Getting Started</h3>
        <nav class="space-y-1">
            <a href="index.html" class="nav-link" data-page="index">Introduction</a>
            <a href="index.html#install" class="nav-link" data-page="install">Installation</a>
        </nav>
    </section>
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Core Modules</h3>
        <nav class="space-y-1">
            <a href="rcon.html" class="nav-link" data-page="rcon">RCON Protocol</a>
            <a href="status.html" class="nav-link" data-page="status">Server Status</a>
            <a href="logs.html" class="nav-link" data-page="logs">Log Engine</a>
        </nav>
    </section>
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Server Management</h3>
        <nav class="space-y-1">
            <a href="management.html" class="nav-link" data-page="management">Power Control</a>
            <a href="scheduling.html" class="nav-link" data-page="scheduling">Schedules</a>
            <a href="stats.html" class="nav-link" data-page="stats">Performance Stats</a>
        </nav>
    </section>
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Advanced</h3>
        <nav class="space-y-1">
            <a href="spark.html" class="nav-link" data-page="spark">Spark Profiler</a>
        </nav>
    </section>
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Player Intelligence</h3>
        <nav class="space-y-1">
            <a href="players.html" class="nav-link" data-page="players">Stats & Profiles</a>
        </nav>
    </section>
    <section>
        <h3 class="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4 px-3">Reference</h3>
        <nav class="space-y-1">
            <a href="models.html" class="nav-link" data-page="models">Models & Errors</a>
        </nav>
    </section>
</div>
`;

document.addEventListener('DOMContentLoaded', () => {
    const sidebarEl = document.getElementById('sidebar-inject');
    if (sidebarEl) {
        sidebarEl.innerHTML = sidebarContent;
        
        // Highlight active page
        const currentPath = window.location.pathname;
        const page = currentPath.split('/').pop().split('.')[0] || 'index';
        const links = sidebarEl.querySelectorAll('.nav-link');
        links.forEach(link => {
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            }
        });
    }

    // Mobile menu logic
    const btn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar-container');
    const overlay = document.getElementById('sidebar-overlay');

    if (btn && sidebar && overlay) {
        btn.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
        });
    }
});
