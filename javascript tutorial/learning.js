document.body.style.background="lightblue";
console.log("Enjoy your stay!");
console.log("895-564=331")
console.log("-Spongebob Squarepants")
function greet(name,city){
    alert("Welcome to "+city + name + "!");
}
greet("Sandy Cheeks", "Bikini Bottom, ");
let citizen = "Patrick Star";
console.log(citizen);
citizen = "Squidward Tentacles";
console.log(citizen);
citizen = "Mr. Krabs";
console.log(citizen);
const maincharacter = "Spongebob Squarepants";
console.log(maincharacter);
let numberOfFriends = 3;
let KrustyKrabOpen = false;
console.log(numberOfFriends>2);
let a = 10
let b = 5
console.log(b**a);
if(numberOfFriends>2){
    console.log("You've met alot of people!");
}else{
    console.log("You should try to meet more people!");
}
while(numberOfFriends<5){
    console.log("Making new friends...");
    numberOfFriends++;
}
for(let i=1;i<5;i++){
    console.log("This is friend number " + i);
}

function unlockCity(city,name){
    alert(city+name+" is now unlocked! Enjoy your stay!");
    document.querySelectorAll('.remove').forEach(element => element.remove());
}

console.log(document.body.style)
document.body.style.color="navy";
// Hiding all elements with class "widget"
let hidecount = 0;
document.querySelectorAll(".widget").forEach(el => {
    el.style.display = "none";
});

function showWidgets() {
    if (hidecount%2==0){
        document.querySelectorAll(".widget").forEach(el => {
            el.style.display = "block";
            hidecount++;
        });
    } else {
        document.querySelectorAll(".widget").forEach(el => {
            el.style.display = "none";
            hidecount++;
        });
    }
}