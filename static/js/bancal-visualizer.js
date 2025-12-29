/**
 * BancalVisualizer - Canvas-based visualization for raised bed gardens
 * Displays a 4m x 1m bed with planted crops according to their spacing and row position
 */

class BancalVisualizer {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas with id "${canvasId}" not found`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        
        // Bed dimensions (in centimeters)
        this.BED_WIDTH_CM = 400;  // 4 meters
        this.BED_HEIGHT_CM = 100; // 1 meter
        
        // Canvas dimensions (in pixels)
        this.canvasWidth = options.width || 800;
        this.canvasHeight = options.height || 200;
        
        // Set canvas size
        this.canvas.width = this.canvasWidth;
        this.canvas.height = this.canvasHeight;
        
        // Calculate scale factor
        this.scaleX = this.canvasWidth / this.BED_WIDTH_CM;
        this.scaleY = this.canvasHeight / this.BED_HEIGHT_CM;
        
        // Colors
        this.colors = {
            bedBackground: '#f5f5dc',  // Beige (soil color)
            bedBorder: '#8B4513',      // Brown
            gridLines: '#d3d3d3',      // Light gray
            rowLines: '#a9a9a9'        // Dark gray
        };
        
        this.cultures = [];
        this.showGrid = options.showGrid !== false;
    }
    
    /**
     * Convert centimeters to canvas pixels
     */
    cmToPixel(cm, axis = 'x') {
        return cm * (axis === 'x' ? this.scaleX : this.scaleY);
    }
    
    /**
     * Draw the base bed structure
     */
    drawBed() {
        const ctx = this.ctx;
        
        // Draw bed background
        ctx.fillStyle = this.colors.bedBackground;
        ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        // Draw border
        ctx.strokeStyle = this.colors.bedBorder;
        ctx.lineWidth = 3;
        ctx.strokeRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        if (this.showGrid) {
            this.drawGrid();
        }
        
        this.drawRowLines();
    }
    
    /**
     * Draw grid lines every 50cm horizontally and 25cm vertically
     */
    drawGrid() {
        const ctx = this.ctx;
        ctx.strokeStyle = this.colors.gridLines;
        ctx.lineWidth = 0.5;
        ctx.setLineDash([5, 5]);
        
        // Vertical lines every 50cm
        for (let cm = 50; cm < this.BED_WIDTH_CM; cm += 50) {
            const x = this.cmToPixel(cm, 'x');
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.canvasHeight);
            ctx.stroke();
        }
        
        // Horizontal lines at 25cm and 75cm (quartiles)
        [25, 75].forEach(cm => {
            const y = this.cmToPixel(cm, 'y');
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.canvasWidth, y);
            ctx.stroke();
        });
        
        ctx.setLineDash([]);
    }
    
    /**
     * Draw row division lines
     */
    drawRowLines() {
        const ctx = this.ctx;
        ctx.strokeStyle = this.colors.rowLines;
        ctx.lineWidth = 1;
        ctx.setLineDash([2, 2]);
        
        // Divide bed into 3 rows
        const rowHeight = this.BED_HEIGHT_CM / 3;
        
        for (let i = 1; i < 3; i++) {
            const y = this.cmToPixel(rowHeight * i, 'y');
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.canvasWidth, y);
            ctx.stroke();
        }
        
        ctx.setLineDash([]);
    }
    
    /**
     * Calculate Y position based on row
     */
    getRowYCenter(rowPosition) {
        const rowHeight = this.BED_HEIGHT_CM / 3;
        const rowMap = {
            'superior': rowHeight / 2,
            'central': rowHeight * 1.5,
            'inferior': rowHeight * 2.5
        };
        return rowMap[rowPosition] || rowMap['central'];
    }
    
    /**
     * Add a culture to visualize
     */
    addCulture(culture) {
        this.cultures.push(culture);
    }
    
    /**
     * Calculate plant positions based on spacing and alignment
     */
    calculatePlantPositions(quantity, spacingCm, rowPosition, alignment = 'center') {
        const positions = [];
        const yCm = this.getRowYCenter(rowPosition);
        
        // Calculate total width needed
        const totalWidth = (quantity - 1) * spacingCm;
        
        // Margin from edges (20cm on each side)
        const EDGE_MARGIN = 20;
        const usableWidth = this.BED_WIDTH_CM - (2 * EDGE_MARGIN);
        
        // Determine starting X position based on alignment
        let startX;
        if (alignment === 'left') {
            startX = EDGE_MARGIN;
        } else if (alignment === 'right') {
            startX = this.BED_WIDTH_CM - totalWidth - EDGE_MARGIN;
        } else { // center (default)
            startX = EDGE_MARGIN + (usableWidth - totalWidth) / 2;
        }
        
        for (let i = 0; i < quantity; i++) {
            const xCm = startX + (i * spacingCm);
            positions.push({
                x: this.cmToPixel(xCm, 'x'),
                y: this.cmToPixel(yCm, 'y')
            });
        }
        
        return positions;
    }
    
    /**
     * Draw a single plant icon
     */
    drawPlant(x, y, icon, color) {
        const ctx = this.ctx;
        const size = 20; // Icon size in pixels
        
        // Draw background circle
        ctx.fillStyle = color || '#4CAF50';
        ctx.beginPath();
        ctx.arc(x, y, size / 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw icon/emoji
        ctx.font = `${size}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(icon, x, y);
    }
    
    /**
     * Draw all cultures
     */
    drawCultures() {
        this.cultures.forEach(culture => {
            const positions = this.calculatePlantPositions(
                culture.quantity,
                culture.spacing,
                culture.row,
                culture.alignment || 'center'
            );
            
            positions.forEach(pos => {
                this.drawPlant(pos.x, pos.y, culture.icon, culture.color);
            });
        });
    }
    
    /**
     * Draw legend
     */
    drawLegend(containerId) {
        if (!this.cultures.length) return;
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        let html = '<div class="bancal-legend mt-2"><strong>Cultivos:</strong><ul class="list-inline mb-0 ms-2">';
        
        this.cultures.forEach(culture => {
            html += `
                <li class="list-inline-item me-3">
                    <span style="font-size: 1.2em;">${culture.icon}</span>
                    <span class="ms-1">${culture.name}</span>
                    <small class="text-muted">(${culture.quantity} plantas, ${culture.spacing}cm)</small>
                </li>
            `;
        });
        
        html += '</ul></div>';
        container.innerHTML = html;
    }
    
    /**
     * Render the complete visualization
     */
    render(legendContainerId = null) {
        this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        this.drawBed();
        this.drawCultures();
        
        if (legendContainerId) {
            this.drawLegend(legendContainerId);
        }
    }
    
    /**
     * Clear all cultures
     */
    clear() {
        this.cultures = [];
        this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        this.drawBed();
    }
}

// Plant color palette (assign colors to different plant types)
const PLANT_COLORS = {
    'Tomate': '#FF6B6B',
    'Pimiento': '#FFA500',
    'Berenjena': '#9370DB',
    'Zanahoria': '#FF8C00',
    'Lechuga': '#90EE90',
    'Cebolla': '#DDA0DD',
    'Haba': '#98D8C8',
    'Guisante': '#98D8C8',
    'Pepino': '#3CB371',
    'Ajo': '#F5F5DC',
    'Patata': '#D2691E',
    'Brócoli': '#228B22',
    'Brokoli': '#228B22',
    'Col': '#7CFC00',
    'Coliflor': '#F5F5F5',
    'Fresa': '#FF69B4',
    'Alcachofa': '#6B8E23',
    'Alcahofa': '#6B8E23',
    'Sandía': '#FF1493',
    'Melón': '#FFD700',
    'default': '#4CAF50'
};

/**
 * Get color for a plant
 */
function getPlantColor(plantName) {
    return PLANT_COLORS[plantName] || PLANT_COLORS['default'];
}
