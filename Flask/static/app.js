// app.js
document.addEventListener('DOMContentLoaded', function () {
    
    var svg = d3.select('#d3-container')
        .append('svg')
        .attr('width', 400)
        .attr('height', 200);

    svg.append('rect')
        .attr('x', 10)
        .attr('y', 10)
        .attr('width', 380)
        .attr('height', 180)
        .attr('fill', 'lightblue');
});
