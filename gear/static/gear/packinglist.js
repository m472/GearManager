
function savePackedFunction() {
    document.getElementById("savePacked").submit();
}

function saveCardinality(element) {
    count = parseInt(element.value);

    if (count > 0) {
        element.parentElement.submit();
    }
    else {
        element.value = 1;
    }
}

