document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('paipan-form');
    const gridContainer = document.getElementById('ziwei-grid');
    const summarySection = document.getElementById('summary-section');
    const analysisResults = document.getElementById('analysis-results');

    // 宫位索引到 Grid 坐标的映射 (Row, Col)
    // 0=寅, 1=卯, 2=辰, 3=巳, 4=午, 5=未, 6=申, 7=酉, 8=戌, 9=亥, 10=子, 11=丑
    const gridPosMap = [
        [4, 1], [3, 1], [2, 1], [1, 1],
        [1, 2], [1, 3], [1, 4], [2, 4],
        [3, 4], [4, 4], [4, 3], [4, 2]
    ];

    let currentAstrolabe = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            date_str: document.getElementById('date').value,
            time_index: parseInt(document.getElementById('time_index').value),
            gender: form.elements['gender'].value,
            date_type: 'solar'
        };

        try {
            showToast('正在排盘...');
            const response = await fetch('/api/paipan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await response.json();
            currentAstrolabe = data.astrolabe;
            renderChart(currentAstrolabe);
            updateSummary(currentAstrolabe);
            summarySection.classList.remove('hidden');
        } catch (err) {
            console.error(err);
            showToast('排盘失败，请检查输入', 'error');
        }
    });

    function renderChart(astrolabe) {
        // 保留中央内容
        const center = gridContainer.querySelector('.center-content');
        gridContainer.innerHTML = '';
        gridContainer.appendChild(center);

        // 更新中央信息
        document.getElementById('val-solar').textContent = astrolabe.solar_date;
        document.getElementById('val-lunar').textContent = astrolabe.lunar_date;

        astrolabe.palaces.forEach((palace, index) => {
            const cell = document.createElement('div');
            cell.className = 'palace-cell';
            const [row, col] = gridPosMap[index];
            cell.style.gridRow = row;
            cell.style.gridColumn = col;

            // 宫位头
            const header = document.createElement('div');
            header.className = 'palace-header';
            header.innerHTML = `<span>${palace.heavenly_stem}${palace.earthly_branch}</span><span>${palace.ages[0]}岁</span>`;
            
            // 宫位名
            const name = document.createElement('div');
            name.className = 'palace-name';
            name.textContent = palace.name + (palace.is_body_palace ? ' (身)' : '');

            // 星耀内容
            const content = document.createElement('div');
            content.className = 'palace-content';

            // 主星
            palace.major_stars.forEach(s => {
                content.appendChild(createStarEl(s, 'major'));
            });
            // 辅星
            palace.minor_stars.forEach(s => {
                content.appendChild(createStarEl(s, 'minor'));
            });
            // 杂耀
            palace.adjective_stars.forEach(s => {
                content.appendChild(createStarEl(s, 'adjective'));
            });

            // 宫位脚
            const footer = document.createElement('div');
            footer.className = 'palace-footer';
            footer.innerHTML = `<span class="decade-range">${palace.decadal.range[0]} - ${palace.decadal.range[1]}</span><span>${palace.boshi12} / ${palace.changsheng12}</span>`;

            cell.appendChild(header);
            cell.appendChild(name);
            cell.appendChild(content);
            cell.appendChild(footer);

            cell.addEventListener('click', () => handlePalaceClick(index, cell));
            gridContainer.appendChild(cell);
        });
    }

    function createStarEl(star, type) {
        const el = document.createElement('div');
        el.className = `star ${type}`;
        el.innerHTML = `
            ${star.name}
            ${star.brightness ? `<span class="brightness">${star.brightness}</span>` : ''}
            ${star.mutagen ? `<span class="mutagen">${star.mutagen}</span>` : ''}
        `;
        return el;
    }

    async function handlePalaceClick(index, cell) {
        // 清除之前的效果
        document.querySelectorAll('.palace-cell').forEach(el => {
            el.classList.remove('highlight-target', 'highlight-surrounded');
        });

        cell.classList.add('highlight-target');

        // 发起三方四正查询
        try {
            const formData = {
                date_str: document.getElementById('date').value,
                time_index: parseInt(document.getElementById('time_index').value),
                gender: document.querySelector('input[name="gender"]:checked').value,
                palace: index
            };
            const response = await fetch('/api/palace/surrounded', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const sp = await response.json();

            // 高亮三方四正
            const allCells = document.querySelectorAll('.palace-cell');
            [sp.opposite.index, sp.wealth.index, sp.career.index].forEach(idx => {
                allCells[idx].classList.add('highlight-surrounded');
            });

            // 更新左侧分析面板
            updateAnalysisPanel(sp);
        } catch (err) {
            console.error(err);
        }
    }

    function updateAnalysisPanel(sp) {
        const getStars = (p) => [...p.major_stars, ...p.minor_stars].map(s => s.name + (s.mutagen ? `(${s.mutagen})` : '')).join(', ') || '无';
        analysisResults.innerHTML = `
            <div class="analysis-box">
                <p><strong>${sp.target.name} (本宫):</strong> ${getStars(sp.target)}</p>
                <p><strong>${sp.opposite.name} (对宫):</strong> ${getStars(sp.opposite)}</p>
                <p><strong>${sp.wealth.name} (财帛):</strong> ${getStars(sp.wealth)}</p>
                <p><strong>${sp.career.name} (官禄):</strong> ${getStars(sp.career)}</p>
            </div>
            <div class="analysis-meta">
                <p>💡 此组合包含三方四正星耀，综合断语可在此扩展。</p>
            </div>
        `;
    }

    function updateSummary(astrolabe) {
        document.getElementById('val-zodiac').textContent = astrolabe.zodiac;
        document.getElementById('val-sign').textContent = astrolabe.sign;
        document.getElementById('val-elements').textContent = astrolabe.five_elements_class;
        document.getElementById('val-soul').textContent = astrolabe.soul;
        document.getElementById('val-body').textContent = astrolabe.body;
        document.getElementById('val-chinese_date').textContent = astrolabe.chinese_date;
    }

    function showToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.style.background = type === 'error' ? 'var(--accent-red)' : 'var(--primary)';
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
});
