<template><web-view :src="url" /></template>
<script>export default { data() { return { url: '' } }, onLoad(query) { this.url = decodeURIComponent(query.url || '') } }</script>
