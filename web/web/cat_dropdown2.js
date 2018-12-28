var subjects_checked = [];
function testCheckbox()
{
  subjects_checked = [];
  for (i = 1 ; i<14 ; i++){
    //console.log("subject"+i.toString());
    var oCheckbox = subjectList.elements["subject"+i.toString()];
    var checkbox_val = oCheckbox.value;
    if (oCheckbox.checked == true)
    {
      subjects_checked.push(oCheckbox.name);
     // console.log("Checkbox with name = " + oCheckbox.name + " and value =" +
     //           checkbox_val + " is checked");
    }
    // else
    // {
    //     console.log("Checkbox with name = " + oCheckbox.name + " and value =" +
    //           checkbox_val + " is not checked");
    // }
  }
 // console.log(checked_subjects);
}

oCheckBox1 = subjectList.elements["one"];
oCheckBox2 = subjectList.elements["two"];
 
testCheckbox();
