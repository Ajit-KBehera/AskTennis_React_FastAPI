import '@testing-library/jest-dom'

// Mock for URL.createObjectURL (used by Plotly)
if (typeof window !== 'undefined') {
  window.URL.createObjectURL = function() { return "mock_url"; };
  window.URL.revokeObjectURL = function() { };
}

// Mock for Canvas (used by Plotly)
// jsdom doesn't support canvas out of the box without the 'canvas' package
// We can mock the getContext method to likely satisfy Plotly's initialization checks
if (typeof HTMLCanvasElement !== 'undefined') {
    HTMLCanvasElement.prototype.getContext = function() {
        return {
            fillRect: function() {},
            clearRect: function() {},
            getImageData: function(x, y, w, h) {
                return {
                    data: new Array(w * h * 4)
                };
            },
            putImageData: function() {},
            createImageData: function() { return []; },
            setTransform: function() {},
            drawImage: function() {},
            save: function() {},
            fillText: function() {},
            restore: function() {},
            beginPath: function() {},
            moveTo: function() {},
            lineTo: function() {},
            closePath: function() {},
            stroke: function() {},
            translate: function() {},
            scale: function() {},
            rotate: function() {},
            arc: function() {},
            fill: function() {},
            measureText: function() {
                return { width: 0 };
            },
            transform: function() {},
            rect: function() {},
            clip: function() {},
        };
    }
}
